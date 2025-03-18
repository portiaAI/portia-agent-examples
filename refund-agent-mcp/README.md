# Portia SDK Refund Agent with MCP

## Introduction

This example demonstrates how to integrate tools from a Model Context Protocol (MCP) server into the Portia SDK. Here we create an Agent that can handle customer service refund requests using a Stripe integration via their [MCP server](https://github.com/stripe/agent-toolkit/tree/main/modelcontextprotocol).

Alongside MCP integrations, this example also demonstrates how [Clarifications](https://docs.portialabs.ai/understand-clarifications) can be used to keep humans in the loop, protecting against unwanted agent actions such as refunding customers payments incorrectly.

Note: Soon we will be adding the ability to express conditionals in Portia Plans, which will make this use-case much more natural. The tasks of requesting human approval and processing refunds should be _conditional_ on the Agent's approval, otherwise skipped. For now they are implemented in a separate tool call whose objective is to request human approval. If the human rejects the refund, that tool will terminate the plan run before we get to the refund issuing step.

You can read more about the tools provided by Portia Cloud in the [Portia Cloud documentation](https://docs.portialabs.ai/), or about the SDK in the [Portia SDK documentation](https://docs.portialabs.ai/docs/portia-sdk-python).

## Prerequisites

Before running this agent, you'll need the following:

- Python 3.11 (or greater): You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- Poetry: We use poetry to manage dependencies. You can install it from [here](https://python-poetry.org/docs/#installation).
- NPM: The Stripe MCP server requires `npx`. `npx` is part of `npm`, instructions to install `npm` can be found [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm). If you run into errors on start-up, check that you can run `npx` commands in your command line. 
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An OpenAI API key: You can get one from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- A Stripe API key: We used a test-mode key which can be setup at [dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)


## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Install dependencies `poetry install`
4. Setup the Stripe payment to refund
    i. Create a Customer with an email address you have access to.
    ii. Create a Product (this can be anything).
    iii. Create a Payment. We did this by issuing an invoice to the Customer from step (i), and then paying the invoice with a Stripe [test card](https://docs.stripe.com/testing)


## Usage

`poetry run python refund_agent.py --email "<replace-with-stripe-customer-email>"` to run the Agent.

You can play around with the refund email by setting the `--request` arg, e.g. `poetry run python refund_agent.py --email "<stripe-email>" --request "I dropped my Hoverboard in the flux-capacitor, can I get a refund?"`

## Understanding the code

### MCP integration

MCP tools are integrated as an extension to the Portia [ToolRegistry](https://docs.portialabs.ai/SDK/portia/tool_registry#toolregistry-objects) class.

```python
McpToolRegistry.from_stdio_connection(
    server_name="stripe",
    command="npx",
    args=[
        "-y",
        "@stripe/mcp",
        "--tools=all",
        f"--api-key={os.environ['STRIPE_API_KEY']}",
    ],
)
```

This spins up the MCP server using the [MCP python SDK](https://github.com/modelcontextprotocol/python-sdk), extracts the tools and automatically converts them to [Portia `Tool` objects](https://docs.portialabs.ai/intro-to-tools).

### Refunds and Approval Clarifications

We want the Agent to read the refund request, compare it with the company's refund policy (see `./refund_policy.txt`) and make a decision autonomously: this is handled in the `RefundReviewerTool` class.

Because refunds involve sending out money, if the Agent thinks a refund _should_ be issued, we want to get a human to review the request along with the Agent's rationale. To achieve this, we can pause execution and wait from a [Clarification](https://docs.portialabs.ai/understand-clarifications) to get a humand to review the request and the Agent's analysis. This is part of the `RefundHumanApprovalTool` class in `refund_agent.py`. If the human passes `ACCEPTED` the refund should be issued, if `REJECTED` the flow will exit!
