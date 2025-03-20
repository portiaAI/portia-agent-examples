# Get Started with Google Tools

## Introduction

This example demonstrates how to use Portia AI with Google Calendar and GMail tools to schedule a meeting and send an email. It demonstrates a number of key features of the [Portia SDK](https://github.com/portia-ai/portia-sdk-python) including explicit planning, clarification and authentication. You can read more about the SDK and these concepts in the [Portia SDK documentation](https://docs.portialabs.ai/SDK/portia).

## Prerequisites

- A Google Calendar and GMail account
- The email address of someone you want to schedule a meeting with
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An LLM API key for a supported model (e.g Anthropic, OpenAI or Mistral)
- We use poetry to manage dependencies. You can install it from [here](https://python-poetry.org/docs/#installation).

## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Install the dependencies by running `poetry install`.
4. Run the `main.py` file by running `poetry run python main.py`.

## Running the example

When you run the `main.py` file, it will prompt you for your email address and the email address of the person who you wish to schedule a meeting with. It will then generate a plan to schedule a meeting and send an email to the recipient and display this to you before proceeding. As it iterates through the plan, you will be prompted to authenticate with Google for calendar and GMail.

## Understanding the code

The `main.py` file is the entry point for the example and has the following key parts:

- Setup: The configuration and tools are setup.
- Generate the plan: The plan is generated from the user query.
- Iterate on the plan: The user is prompted to review the plan and provide additional guidance if needed.
- Execute the plan: The plan is executed and the user is prompted to authenticate with Google for calendar and GMail.
- Handle clarifications: [Clarifications](https://docs.portialabs.ai/understand-clarifications) are a core abstraction within the Portia SDK and allow for a structured conversation with the user. The code in the example shows how you can handle different types of abstraction that are returned by the SDK.
