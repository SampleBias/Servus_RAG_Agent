import ollama

output = ollama.generate(model='phi', prompt='hello world')
response = output['response']

print(response)