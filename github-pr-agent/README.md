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
2. Install dependencies:
   ```bash
   cd github-pr-agent
   pip install -e .
   ```
3. Create a `.env` file based on `.env.example` and fill in your API keys:
   ```
   PORTIA_API_KEY="your-portia-api-key"
   OPENAI_API_KEY="your-openai-api-key"
   GITHUB_TOKEN="your-github-personal-access-token"
   ```
   
   Note: Your GitHub token needs to have the `repo` scope to read PRs and post comments.

## Usage

Run the agent:

```bash
python agent.py
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