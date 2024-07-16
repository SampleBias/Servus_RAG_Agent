import ollama

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

while True:
    prompt = input("USER: \n")
    
    if prompt.lower() == 'exit':
        print("Ending conversation. Goodbye!")
        break
    
    convo.append({'role': 'user', 'content': prompt})
    
    try:
        output = ollama.chat(model='llama', messages=convo)
        response = output['message']['content']
        
        print(f"ASSISTANT: \n{response}\n")
        
        convo.append({'role': 'assistant', 'content': response})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
