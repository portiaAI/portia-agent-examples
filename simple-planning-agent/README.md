# Portia simplest planning example

## Introduction
The purpose of this agent is just to check that you've got Portia installed correctly with minimal API key requirements.

## Prerequisites

Before running this agent, you'll need the following:

- Python 3.11 (or greater): You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- An LLM API key. We <a href="https://docs.portialabs.ai/manage-config#api-keys">support</a> all of the major LLMs. Set your API key in the .env file using e.g OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY or others.

## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Run the example by doing `uv run main.py`