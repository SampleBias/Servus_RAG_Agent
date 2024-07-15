import ollama run phi3:mini

output = ollama.generate(model='llama', prompt='hello world')
response = output['response']

print(response)
