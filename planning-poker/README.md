# Planning Poker Agent

## Introduction

This example demonstrates how to use Portia AI to build an agent that performs planning poker estimation for Linear tickets. The agent retrieves tickets from Linear using Portia MCP cloud tools, analyzes them from multiple developer perspectives (frontend, backend, and DevOps), and provides planning poker estimates with detailed reasoning.

The agent uses different personas to simulate a team-based planning poker session, where each "developer" provides their estimate based on their area of expertise. This helps create more comprehensive and realistic estimates for development tasks.

## Prerequisites

- Python 3.12: You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- Access to Linear with tickets to estimate
- We use uv to manage dependencies. You can install it from [here](https://docs.astral.sh/uv/getting-started/installation/).

## Setup

1. Clone the repository and select this folder.
2. Set your API keys as environment variables or create a `.env` file:
   ```
   PORTIA_API_KEY=your_portia_api_key_here
   ```
3. Install the dependencies by running `uv sync`.
4. Create a `context.md` file with relevant codebase context to help with estimation.
5. Run the agent by running `uv run python main.py`.

## Running the example

The agent will:
1. Retrieve tickets from Linear using the Portia MCP cloud tools
2. Filter tickets based on the specified type (default: "Async Portia")
3. For each ticket, estimate the size using three different developer personas:
   - Frontend developer
   - Backend developer  
   - DevOps engineer
4. Output the estimates with reasoning for each perspective

The planning poker estimates use the following sizing scale:
- 1D (1 Day)
- 3D (3 Days)
- 5D (5 Days)
- 7D (7 Days)
- 10D (10 Days)
- TLTE (Too Large To Estimate)

## Understanding the code

The agent uses several key components:

- **Linear Integration**: Uses Portia MCP cloud tools to fetch tickets from Linear
- **Multi-Persona Estimation**: Simulates different developer perspectives for comprehensive estimates
- **Structured Output**: Uses Pydantic models to ensure consistent estimation format
- **Context-Aware Analysis**: Incorporates codebase context to provide more accurate estimates

The estimation process follows a planning poker methodology where each "developer" provides their estimate based on their expertise, helping to identify potential challenges and assumptions from different technical perspectives.
