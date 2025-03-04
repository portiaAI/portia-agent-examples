# AI Research Agent

## Introduction

This example demostrates how to use Portia AI to build an agent that can receive emails about a topic, summarise them and post the summary to a slack channel once per day. It utilises the [Gmail tools](https://docs.portialabs.ai/gmail-tools) and [Slack tools](https://docs.portialabs.ai/portia-tools/slack/) provided by Portia Cloud to read emails about 'AI' and post the summary to slack.

At Portia, we have an email inbox that is signed up to multiple AI newsletters. We then use this agent to summaries the emails and post to our #ai-news slack channel once per day.

## Prerequisites

- A Gmail account to receive emails from
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An OpenAI API key (or equivalent for another LLM provider)
- A slack client ID and secret: You can get these by followign the steps [here](https://docs.portialabs.ai/portia-tools/slack/send-message#configure-your-slack-tools-with-portia-ai)
- We use poetry to manage dependencies. You can install it from [here](https://python-poetry.org/docs/#installation).

## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Enter the slack client ID and secret into the [Portia dashboard](https://app.portialabs.ai/dashboard/org-settings) to allow Portia to interact with slack.
4. Install the dependencies by running `poetry install`.
5. Run the `agent.py` file by running `poetry run python agent.py`.

## Running the example

The first time you run the agent, you will be prompted to authenticate with Google. Once this has been done once, Portia cloud will handle future authentications for you and so the plan should run without any clarifications.