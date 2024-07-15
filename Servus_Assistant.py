import ollama

output = ollama.generate(model='llama', prompt='hello world')
response = output['response']

print(response)
