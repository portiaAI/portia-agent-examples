# Vehicle Assistance Chat Agent

## Introduction

This example demonstrates how to create a specialized chat interface for a Vehicle Assistance agent using Portia AI and Streamlit. The agent focuses on three specific vehicle assistance services: instructions and how-to queries, driving license applications, and vehicle tax payments. It demonstrates key features of the [Portia SDK](https://github.com/portiaAI/portia-sdk-python) including intelligent query classification, structured data collection, and interactive clarifications.

## Prerequisites

- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An LLM API key for a supported model (e.g Anthropic, OpenAI or Mistral)
- A Tavily API key from https://app.tavily.com/home
- We use `uv` to manage dependencies. You can install it from [here](https://docs.astral.sh/uv/getting-started/installation/).

## Setup

1. Clone the repository and navigate to the `vehicle-assisstance-agent` folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Install dependencies: `uv sync`

## Running the example

Run the chat application using the provided script:

```bash
./run_app.sh
```

Alternatively, you can run it directly with:
```bash
uv run streamlit run app.py
```

The chat interface will open in your browser at `http://localhost:8501`.
