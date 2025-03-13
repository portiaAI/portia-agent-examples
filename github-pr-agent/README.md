# GitHub PR Agent

A Portia agent that analyzes GitHub PRs and provides feedback.

## Features

This agent:
1. Reads the latest PR for the portiaAI/platform repo
2. Uses an LLM to create a description for it
3. Uses an LLM to give feedback on the code
4. Comments on the PR

## Setup

1. Clone this repository
2. Install dependencies using Poetry:
   ```bash
   cd github-pr-agent
   poetry install
   ```
   
   If you don't have Poetry installed, you can install it following the instructions at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)

3. Create a `.env` file based on `.env.example` and fill in your API keys:
   ```
   PORTIA_API_KEY="your-portia-api-key"
   OPENAI_API_KEY="your-openai-api-key"
   GITHUB_TOKEN="your-github-personal-access-token"
   ```
   
   To get these API keys:
   - **PORTIA_API_KEY**: Sign up at [app.portialabs.ai](https://app.portialabs.ai) and create an API key
   - **OPENAI_API_KEY**: Sign up at [platform.openai.com](https://platform.openai.com) and create an API key
   - **GITHUB_TOKEN**: Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens) and create a token with the `repo` scope to read PRs and post comments

## Usage

Run the agent using Poetry:

```bash
cd github-pr-agent
poetry run python agent.py
```

The agent will:
1. Get the latest PR from the portiaAI/platform repository
2. Generate a description for the PR
3. Analyze the code changes and provide feedback
4. Post a comment on the PR with the description and feedback

## Customization

You can modify the `agent.py` file to:
- Change the target repository (modify the `REPO` variable)
- Adjust the analysis criteria
- Change the LLM model used (modify the `config` setup)

## License

See the LICENSE file in the root of this repository.