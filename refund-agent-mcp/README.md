# Portia SDK Refund Agent with MCP

This agent analyzes a mock email `inbox.txt` sent by a customer against a mock refund policy `refund_policy.txt`. If it believes the refund should proceed, it will present it's rationale to the human operative (you!) for approval via the command line. Once approved, the refund agent will use the Stripe MCP server to retrieve the payment intent for the customer, and execute the refund. Finally, it will send the customer an email on behalf of the human operative summarizing what it has done.

## Introduction

This example demonstrates how to integrate tools from a Model Context Protocol (MCP) server into the Portia SDK using the Portia Tool Registry. Here we create an Agent that can handle customer service refund requests using a Stripe integration via their [MCP server](https://docs.stripe.com/building-with-llms#mcp-remote). The MCP server for the default example can be set up in 3-clicks on your personalized [Portia tool registry](https://app.portialabs.ai/dashboard/tool-registry).

There are also two alternative versions of this example in this directory:
1. Under `refund_agent_with_local_mcp.py`, the agent works similarly but uses the [local variety of Stripe MCP server](https://github.com/stripe/agent-toolkit/tree/main/modelcontextprotocol) through `npx`. There are instructions at the end for how to run this particular variant of the agent.
2. Under `refund_agent_plan_builder.py`, we demonstrate how you can rely on the declarative `PlanBuilderV2` interface to define the plan that you want the refund agent to pursue. More on this approach to planning can be found in our docs [here](https://docs.portialabs.ai/build-plan).

Alongside MCP integrations, this example also demonstrates how [Clarifications](https://docs.portialabs.ai/understand-clarifications) can be used to keep humans in the loop, protecting against unwanted agent actions such as refunding customers payments incorrectly.

You can read more about the tools provided by Portia Cloud in the [Portia Cloud documentation](https://docs.portialabs.ai/), or about the SDK in the [Portia SDK documentation](https://docs.portialabs.ai/SDK/portia).

## Prerequisites

Before running this agent, you'll need the following:

- Python 3.11 (or greater): You can download it from [python.org](https://www.python.org/downloads/) or install it using [pyenv](https://github.com/pyenv/pyenv)
- UV: We use uv to manage dependencies. You can install it from [here](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- A Portia AI API key: You can get one from [app.portialabs.ai](https://app.portialabs.ai) > API Keys.
- An OpenAI API key: You can get one from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
- A Stripe API key: We used a test-mode key which can be setup at [dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys). Note that you want the secret key, starting `sk-[test]`.
- Stripe configured in your Portia tool registry: You can enable it by going to the [Portia tool registry](https://app.portialabs.ai/dashboard/tool-registry) in the dashboard, click on Stripe and enter your API key from the previous step to enable it.


## Setup

1. Clone the repository and select this folder.
2. Copy the `.env.example` file to `.env` and add your API keys to it.
3. Setup the Stripe payment to refund. You can use `uv run stripe_setup.py --email <test email>`, or follow these steps:
    i. Create a Customer with an email address you have access to.
    ii. Create a Product (this can be anything).
    iii. Create a Payment. We did this by issuing an invoice to the Customer from step (i), and then paying the invoice with a Stripe [test card](https://docs.stripe.com/testing)


## Usage

`uv run refund_agent.py --email "<replace-with-stripe-customer-email>"` to run the Agent.

You can play around with the refund email by setting the `--request` arg, e.g. `uv run refund_agent.py --email "<stripe-email>" --request "I dropped my Hoverboard in the flux-capacitor, can I get a refund?"`

## Understanding the code

### MCP integration

Once set up in the Portia Tool Registry, the `DefaultToolRegistry` will automatically fetch Stripe (and any of the tools you have enabled in the registry). These are then provided to the planner to produce the final plan meeting the users query.

### Refunds and Approval Clarifications

We want the Agent to read the refund request, compare it with the company's refund policy (see `./refund_policy.txt`) and make a decision autonomously: this is handled in the `RefundReviewerTool` class.

Because refunds involve sending out money, if the Agent thinks a refund _should_ be issued, we want to get a human to review the request along with the Agent's rationale. To achieve this, we can pause execution and wait from a [Clarification](https://docs.portialabs.ai/understand-clarifications) to get a human to review the request and the Agent's analysis. This implemented using [`ExecutionHooks`](https://docs.portialabs.ai/execution-hooks) by setting the `before_tool_call` property to invoke the method `clarify_on_tool_calls("mcp:stripe:create_refund")` and raise the required clarification. If the end user replied with the affirmative (types in 'y' in the CLI), the workflow proceeds otherwise it exits without creating the refund.

In this particular case, we're using the CLI to elicit responses from the human, but you can build end to end applications that handle clarifications and communication back and forth with the user instead.

### Authentication

The agent recognises that in the last step of the flow, it needs to send an email using GMail. Because GMail uses OAuth, it authenticates you as the user before it starts executing so that it can complete as much of the flow autonomously as possible.


## Local refund agent specific instructions

### Local MCP pre-requisites

- NPM: The Stripe MCP server requires `npx`. `npx` is part of `npm`, instructions to install `npm` can be found [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm). If you run into errors on start-up, check that you can run `npx` commands in your command line. 

### Usage

`uv run refund_agent_with_local_mcp.py --email "<replace-with-stripe-customer-email>"` to run the Agent.

### Understanding the code

MCP tools are integrated as an extension to the Portia [ToolRegistry](https://docs.portialabs.ai/SDK/portia/tool_registry#toolregistry-objects) class.

```python
McpToolRegistry.from_stdio_connection(
    server_name="stripe",
    command="npx",
    args=[
        "-y",
        "@stripe/mcp",
        "--tools=all",
        f"--api-key={os.environ['STRIPE_TEST_gAPI_KEY']}",
    ],
)
```

This spins up the MCP server using the [MCP python SDK](https://github.com/modelcontextprotocol/python-sdk), extracts the tools and automatically converts them to [Portia `Tool` objects](https://docs.portialabs.ai/intro-to-tools).


## Evals

The refund agent ships with a builtin set of Evals using SteelThread - our evals product. As long as you have an `OPENAI_API_KEY` and `PORTIA_API_KEY` set up you can run the evals. This will download test cases from Portia, run them against the agent and report the results back to Portia. You will be able to see the results [in the dashboard](https://app.portialabs.ai/dashboard/evals).

**Warning**: Given the time the agent takes to run it can take up to ~10 minutes to run the evals. You may wish to edit the `iterations` and `max_concurrency` config in `evals/evals.py` to speed this up. 

You can run these with 

```
uv run evals/evals.py
```
