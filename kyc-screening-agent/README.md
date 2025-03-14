# KYC Screening Agent

This example demonstrates how to build a Know Your Customer (KYC) screening agent using Portia AI. The agent performs the following tasks:

1. Takes a person's name as input
2. Searches the web for information about the person
3. Analyzes search results to identify potential illegal activities
4. Calculates a risk factor score
5. Makes a KYC assessment based on the findings

## Features

- Web search integration to gather information about individuals
- LLM-based analysis of web content to identify potential illegal activities
- Risk assessment scoring (simulated for this example)
- Comprehensive KYC assessment report generation

## Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- Portia API key (from [app.portialabs.ai](https://app.portialabs.ai))
- LLM API key (OpenAI, Mistral, or Anthropic)

## Setup

1. Clone this repository
2. Navigate to the `kyc-screening-agent` directory
3. Copy `.env.example` to `.env` and add your API keys
4. Install dependencies with Poetry:

```bash
poetry install
```

## Usage

Run the KYC screening agent:

```bash
poetry run python kyc_agent.py
```

Follow the prompts to enter the name of the person you want to screen. The agent will:

1. Generate a plan for the KYC screening process
2. Execute the plan, which includes web searches and content analysis
3. Calculate a risk factor score
4. Provide a detailed KYC assessment report

## How It Works

The agent uses Portia AI to orchestrate the KYC screening process:

1. **Web Search**: The agent searches the web for information about the person using Portia's built-in web search tools.
2. **Content Analysis**: For each search result, the agent uses an LLM to analyze the content and determine if there's evidence of illegal activity, rating it on a scale from "definitely not" to "definitely".
3. **Risk Assessment**: The agent uses a custom Risk Assessment Tool to calculate a risk factor score (0-10) for the person.
4. **KYC Assessment**: Based on the web search analysis and risk factor score, the agent makes a final assessment on whether the person passes the KYC check.

## Customization

In a real-world scenario, you would replace the dummy Risk Assessment Tool with an actual risk assessment API or database lookup. You could also extend the agent to:

- Check against sanctions lists
- Verify identity documents
- Perform additional background checks
- Integrate with your existing KYC systems