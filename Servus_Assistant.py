import ollama

convo = []

print("Chat with the AI. Type 'exit' to end the conversation.")

while True:
    prompt = input("USER: ")
    
    if prompt.lower() == 'exit':
        print("Ending conversation. Goodbye!")
        break
    
    convo.append({'role': 'user', 'content': prompt})
    
    try:
        output = ollama.chat(model='llama', messages=convo)
        response = output['message']['content']
        
        print(f"ASSISTANT: {response}\n")
        
        convo.append({'role': 'assistant', 'content': response})
    except Exception as e:
        print(f"An error occurred: {str(e)}")
