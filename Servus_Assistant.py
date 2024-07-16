import ollama
import chromadb

client = chromadb.Client()
message_history = [
    {
        'id': 1,
        'prompt': 'What is my name?',
        'response': 'Your name is Austin, known online as AI Austin.'
    },
    {
        'id': 2,
        'prompt': 'What is the square root of 9876?',
        'response': '99.37806559904'
    },
    {
        'id': 3,
        'prompt': 'What kind of dog do I have?',
        'response': 'Your dog Bernardo he is a pug. he is a light brindle and will never leave you alone'
    }
]
convo = []

def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt})
    response = ''
    stream = ollama.chat(model='llama3', messages=convo, stream=True)
    print('\nASSISTANT:')
    
    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)
    
    print('\n')
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
        response = ollama.embeddings


while True:
    prompt = input('USER: \n')
    stream_response(prompt=prompt)
