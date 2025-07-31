# AI Research Agent

## Introduction

This example demonstrates how to use Portia AI to build an agent that can receive emails about a topic, summarise them and then create a short (2-3 mins) podcast from them which is shared to slack / discord. It utilises the [Gmail tools](https://docs.portialabs.ai/gmail-tools) and [Slack tools](https://docs.portialabs.ai/portia-tools/slack/) provided by Portia Cloud to read emails about 'AI' and post the summary to slack, as well as creating a new local [Podcastfy](https://github.com/souzatharsis/podcastfy/tree/main) for podcast creation.

At Portia, we have an email inbox that is signed up to multiple AI newsletters. We then use this agent to summarise the emails and post the summary along with the podcast to our #ai-news slack channel and to our discord server once per day. More details can be found in [this blog post](TODO).

## Prerequisites

- A Gmail account to receive emails from
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An OpenAI API key
- If you want to use Gemini for the podcast creation (this can give better quality speech): A Gemini API key
- A slack client ID and secret: You can get these by following the steps [here](https://docs.portialabs.ai/portia-tools/slack/send-message#configure-your-slack-tools-with-portia-ai)
- We use poetry to manage dependencies. You can install it from [here](https://python-poetry.org/docs/#installation).
- If you want the agent to post to discord as well as slack, you will need a discord bot token and a discord channel id. Follow the steps [here](https://discord.com/developers/docs/quick-start/getting-started) to create a Discord bot and get the token. You should also follow the steps to install the bot into your server. Then, follow the steps [here](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID) to find the channel ID of the channel you want your bot to be active in. Note that you'll need to enable developer mode in Discord to get the IDs.

## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Enter the slack client ID and secret into the [Portia dashboard](https://app.portialabs.ai/dashboard/org-settings) to allow Portia to interact with slack.
4. Install the dependencies by running `poetry install`.
5. Install 'ffmpeg' by following the steps [here](https://chatgpt.com/share/67cf7d0f-fd38-8007-9d94-2bae48fd7311) - this is needed for the podcast generation.
6. If you want to improve the quality of the speech in your podcast, follow the steps [here](https://github.com/souzatharsis/podcastfy/blob/a68ea95e96952f34338e86c8ef6395f402d53830//usage/config.md#setting-up-google-tts-model) to set up a Gemini API key capable of using Google's Multi-Speaker voices, and out this key into your .env fila as: `GEMINI_API_KEY=<key>`.
7. If you only want the agent to post to slack, run the `agent.py` file by running `poetry run python agent.py`. If you would also like to post to discord, run `poetry run python discord_bot.py`

## Running the example

The first time you run the agent, you will be prompted to authenticate with Google. Once this has been done once, Portia cloud will handle future authentications for you and so the plan should run without any clarifications. You can then set this up to run daily as a cron job. There are many way to do this - at Portia, we use a scheduled Github Action. For this, you'll need to add your PORTIA_API_KEY and OPENAI_API_KEY to the Github secrets by following the steps [here](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) and then setup the workflow using the code in `.github/workflows/run.yml`.
