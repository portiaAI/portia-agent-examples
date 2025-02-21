# Portia SDK Discord Bot

## Introduction

This example demonstrates how to use Portia AI to build a Discord bot that uses public documentation and Github issues to answer user questions. It utilises the [Github Tools](https://docs.portialabs.ai/github-tools) provided by Portia Cloud to retrieve Github issues alongside a locally-implemented RAG tool that uses [Weaviate](https://weaviate.io/) to load and retrieve information from the Portia SDK documentation. You can read more about the tools provided by Portia Cloud in the [Portia Cloud documentation](https://docs.portialabs.ai/), or about the SDK in the [Portia SDK documentation](https://docs.portialabs.ai/docs/portia-sdk-python).

## Prerequisites

Before running this discord bot, you'll need the following:

- Python 3.12: You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- Poetry: We use poetry to manage dependencies. You can install it from [here](https://python-poetry.org/docs/#installation).
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An OpenAI API key: You can get one from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- A Weaviate URL & API key: Follow the steps [here](https://weaviate.io/developers/wcs/create-instance) to create a Weaviate instance and retrieve the URL and API key. Note that you'll need the admin API key as we'll be loading data into Weaviate as well as reading from it.
- A Discord server ID and channel ID: Follow the steps [here](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID) to find the server ID and channel ID
of the server and channel you want your bot to be active in. Note that you'll need to enable developer mode in Discord to get the IDs.
- A Discord bot token: Follow the steps [here](https://discord.com/developers/docs/quick-start/getting-started) to create a Discord bot and get the token. You should also follow the steps to install the bot into your server.


## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Install dependencies `poetry install`
4. Load the docs into your Weaviate instance with `poetry run python -m bot.loader`
5. Run the bot with `poetry run python -m bot.discord_server`
6. You can then enter `/ask <question>` in the your discord channel to ask the bot a question.

## Usage
`docker compose up` to start a local instance of Weaviate. You can then set the `WEAVIATE_URL` in the env file to `localhost` and leave the `WEAVIATE_API_KEY` empty to use this local instance.
`poetry run python -m bot.loader` to load the Portia SDK documentation into the vector database.
`poetry run python -m bot.discord_server` to run the bot.
`/ask <question>` to ask the bot a question on discord.

## Understanding the code

### Loading data into Weaviate

`loader.py` is the entry point for the loader script. It recursively visits and collects pages from the Portia SDK documentation at https://docs.portialabs.ai. It then calls `insert_docs_into_weaviate` which chunks the text and then inserts it into Weaviate, where an OpenAI embedding model is used to embed the text before it is stored.

Once this is done, you can use the explorer in Weaviate to view the data that has been loaded.

### Running the bot

`discord_server.py` is the entry point for the bot, defining when the bot is called from Discord. When the `/ask` command is used in the #ask-questions channel, the `get_answer` function in `ask.py` is called.

Inside `ask.py`, a Portia agent is kicked off to answer the question. To answer the question, the agent utilises the tools in the Portia Cloud tool registry (which includes a tool for searching Github issues) as well as the `RAGQueryDBTool` tool defined in `weaviate.py`, which queries the Portia SDK docs that we have loaded into Weaviate.
