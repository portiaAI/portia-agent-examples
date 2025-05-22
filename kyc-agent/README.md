# Portia KYC Agent

## Introduction
This agent shows the advantages of policy driven filtering within the KYC domain. It loads risks up for a given customer and then triages them against a policy. 

## Prerequisites

Before running this agent, you'll need the following:

- Python 3.11 (or greater): You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- An LLM API key. We <a href="https://docs.portialabs.ai/manage-config#api-keys">support</a> all of the major LLMs. Set your API key in the .env file using e.g OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY or others.

## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Run the example by doing `uv run main.py`