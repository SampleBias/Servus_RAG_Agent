# Servus_RAG_Agent

Servus_RAG_Agent is an intelligent AI assistant that utilizes Retrieval-Augmented Generation (RAG) to provide context-aware responses. This assistant has memory of past conversations and can recall relevant information to enhance its responses.

## Features

- Conversational AI assistant powered by the Llama3 model
- Memory storage and retrieval using a vector database (ChromaDB)
- PostgreSQL database for storing conversation history
- Ability to recall relevant past conversations
- Custom commands for memory management

## Requirements

To run this project, you need to have the following dependencies installed:

## Setup

1. Ensure you have Python installed on your system.
2. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
3. Set up a PostgreSQL database:
   a. Install PostgreSQL for your operating system (macOS, Windows, or Linux) from the official website: https://www.postgresql.org/download/
   b. Start the PostgreSQL service:
      - On macOS: `brew services start postgresql` (if installed via Homebrew)
      - On Windows: Open the Start menu and search for "Services". Find "PostgreSQL" in the list and click "Start".
   c. Create a new database named `memory_agent`:
      - Open a terminal or command prompt
      - Connect to PostgreSQL: `psql -U postgres`
      - Create the database: `CREATE DATABASE memory_agent;`
      - Exit psql: `\q`
   d. Update the database credentials in your configuration file:
   ```python:Servus_Assistant.py
   DB_HOST = "localhost"
   DB_PORT = "5432"
   DB_NAME = "memory_agent"
   DB_USER = "your_username"
   DB_PASSWORD = "your_password"
   ```
   Make sure to replace `your_username` and `your_password` with secure credentials for production use.

4. Run the main script:
   ```
   python RAG_Assistant_Local.py or the RAG_Assistant.py I think both work well, so try them both out.
   ```

## Usage

Once the assistant is running, you can interact with it using the following commands:

- Regular conversation: Simply type your message and press Enter.
- Recall memory: Start your message with `/recall` to prompt the assistant to search its memory for relevant information.
- Forget last conversation: Type `/forget` to remove the last conversation from memory.
- Memorize information: Use `/memorize` followed by the information you want to store.


## How It Works

1. The assistant uses Ollama for text generation and embeddings.
2. ChromaDB is used as a vector database to store and retrieve conversation embeddings.
3. PostgreSQL stores the full conversation history.
4. When a user asks a question, the system:
   a. Generates relevant search queries
   b. Retrieves similar past conversations from the vector database
   c. Classifies the relevance of retrieved information
   d. Incorporates relevant context into the response

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This is an AI assistant and should be used responsibly. Always verify important information and do not rely solely on the assistant for critical decisions.