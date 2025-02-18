# Portia SDK Discord Bot

A Discord bot that uses RAG (Retrieval Augmented Generation) to answer questions about the Portia SDK documentation.

## Setup

1. Clone the repository
2. Install dependencies `poetry install`
3. Create a `.env` file and add your API keys
4. Run the bot with `poetry run python discord_server.py`

## Usage
`docker compose up` to start the vector database.
`poetry run python loader.py` to load the Portia SDK documentation into the vector database.
`poetry run python discord_server.py` to run the bot.
`/ask <question>` to ask the bot a question on discord.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| DISCORD_BOT_TOKEN | Your Discord bot token from the Discord Developer Portal | Yes |
| OPENAI_API_KEY | Your OpenAI API key for embeddings and completions | Yes |
| WEAVIATE_API_KEY | Your Weaviate API key | Yes |
| WEAVIATE_URL | Your Weaviate URL | Yes |