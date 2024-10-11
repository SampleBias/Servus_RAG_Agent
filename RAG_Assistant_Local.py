import ollama
import chromadb
import psycopg
import ast
from colorama import Fore 
from tqdm import tqdm
from psycopg.rows import dict_row

client = chromadb.Client()

system_prompt = (
    'You are an AI assistant that has memory of every conversation you have ever had with this user. '
    'On every prompt from the user, the system has checked for any relevant messages you have had with the user. '
    'If any embedded previous conversations are attached, use them for context to responding to the user, '
    'if the context is relevant and useful to responding. If the recalled conversations are irrelevant, '
    'disregard speaking about them and respond normally as an AI assistant. Do not talk about recalling conversations. '
    'Just use any useful data from the previous conversations and respond normally as an intelligent AI assistant.'
)
convo = [{'role': 'system', 'content': system_prompt}]

DB_PARAMS = {
    'dbname': 'memory_agent',
    'user': 'example_user',
    'password': 'add password',
    'host': 'localhost',
    'port': '5432'
}

def connect_db():
    return psycopg.connect(**DB_PARAMS)

def fetch_conversations():
    with connect_db() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute('SELECT * FROM conversations')
            return cursor.fetchall()

def store_conversations(prompt, response):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)',
                (prompt, response)
            )
        conn.commit()

def remove_last_conversation():
    with connect_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM conversations WHERE id = (SELECT MAX(id) FROM conversations)')
        conn.commit()

def stream_response(prompt):
    response = ''
    stream = ollama.chat(model='llama3', messages=convo, stream=True)
    print(Fore.LIGHTGREEN_EX + '\nASSISTANT:')
    
    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)
    
    print('\n')
    store_conversations(prompt=prompt, response=response)
    convo.append({'role': 'assistant', 'content': response})

def create_vector_db(conversations):
    vector_db_name = 'conversations'
    
    try:
        client.delete_collection(name=vector_db_name)
    except ValueError:
        pass

    vector_db = client.create_collection(name=vector_db_name)

    for c in conversations:
        serialized_convo = f"prompt: {c['prompt']} response: {c['response']}"
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']
    
        vector_db.add(
            ids=[str(c['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )

def retrieve_embeddings(queries, results_per_query=2):
    embeddings = set()

    for query in tqdm(queries, desc='Processing queries to vector database'):
        response = ollama.embeddings(model='nomic-embed-text', prompt=query)
        query_embeddings = response['embedding']

        vector_db = client.get_collection(name='conversations')
        results = vector_db.query(query_embeddings=[query_embeddings], n_results=results_per_query)
        best_embeddings = results['documents'][0]

        for best in best_embeddings:
             if best not in embeddings:
                 if 'yes' in classify_embedding(query=query, context=best):
                      embeddings.add(best)

    return embeddings

def create_queries(prompt):
    query_msg = [
        'You are a first principle reasoning search query AI agent.',
        'Your list of search queries will be ran on an embedding database of all your conversations',
        'you have ever had with the user. With first principles create a Python list of queries to',
        'search the embeddings database for any data that would be necessary to have access to in',
        'order to correctly respond to the prompt. Your response must be a Python list with no syntax errors.',
        'Do not explain anything and do not ever generate anything but a perfect syntax Python list'
    ]
    query_convo = [
        {'role': 'system', 'content': '\n'.join(query_msg)},
        {'role': 'user', 'content': 'Write an email to my car insurance company and create a persuasive request for them to lower my premium.'},
        {'role': 'assistant', 'content': "['What is the user's name?', 'What is the user's current auto insurance provider?', 'What is their current premium amount?']"},
        {'role': 'user', 'content': 'how can i convert the speak function in my llama3 python voice assistant to use pyttsx3 instead?'},
        {'role': 'assistant', 'content': "['Llama3 voice assistant', 'Python voice assistant', 'OpenAI TTS', 'openai speak']"},
        {'role': 'user', 'content': prompt}
    ]
    response = ollama.chat(model='llama3', messages=query_convo)
    print(Fore.YELLOW + f'\nVector database queries: {response["message"]["content"]} \n')

    try:   
        return ast.literal_eval(response['message']['content'])
    except:
        return [prompt]  

def classify_embedding(query, context):    
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You will not respond as an AI assistant. You only respond "yes" or "no". '
        'Determine whether the context contains data that directly is related to the search query. '
        'If the context is seemingly exactly what the search query needs respond "yes"; if it is anything but directly '
        'related respond "no". DO NOT RESPOND "yes" unless the content is highly relevant to the search query.'
    )
    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': f'SEARCH QUERY: What is the user\'s name? \n\nEMBEDDED CONTEXT: You are James, Destroyer of worlds. How can I help you?'},
        {'role': 'assistant', 'content': 'yes'},
        {'role': 'user', 'content': f'SEARCH QUERY: Llama3 Python Voice Assistant \n\nEMBEDDED CONTEXT: Siri is a voice assistant.'},
        {'role': 'assistant', 'content': 'no'},
        {'role': 'user', 'content': f'SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context}'}
    ]

    response = ollama.chat(model='llama3', messages=classify_convo)

    return response['message']['content'].strip().lower()

def recall(prompt):
    queries = create_queries(prompt=prompt)
    embeddings = retrieve_embeddings(queries=queries)
    convo.append({'role': 'user', 'content': f'MEMORIES: {embeddings} \n\n USER PROMPT: {prompt}'})
    print(f'\n{len(embeddings)} message:response embeddings added for context.')

def main():
    conversations = fetch_conversations() 
    create_vector_db(conversations=conversations)

    while True:
        prompt = input(Fore.CYAN + 'USER: \n')

        if prompt[:7].lower() == '/recall':
            prompt = prompt[8:]
            recall(prompt=prompt)
            stream_response(prompt=prompt)
        elif prompt[:7].lower() == '/forget':
            remove_last_conversation()
            convo.pop()  # Remove the last user message
            print('\n')
        elif prompt[:9].lower() == '/memorize':
            prompt = prompt[10:]
            store_conversations(prompt=prompt, response='Memory stored.')
            print('\n')
        else:
            convo.append({'role': 'user', 'content': prompt})
            stream_response(prompt=prompt)

if __name__ == "__main__":
    main()