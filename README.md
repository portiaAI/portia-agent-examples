# Portia AI Examples

This repo contains example code demonstrating how to use Portia AI SDK and the Portia cloud tool library.

Portia AI is an open source developer framework for stateful, authenticated agentic workflows.
If you haven't checked it out already, check out our [SDK repo](https://github.com/portiaAI/portia-sdk-python) and give us a ⭐!

## [Getting Started with Portia](https://github.com/portiaAI/portia-agent-examples/tree/main/getting-started/)

An introduction to the Portia SDK that walks you through the basics of creating an agent, defining tasks, and executing plans.
This project demonstrates fundamental concepts like:

- GitHub OAuth integration for repository interactions
- Using tools with end user context.
- Model Context Protocol (MCP) integration
- Browser automation for web interactions

Perfect for newcomers to understand the core concepts of Portia before diving into more complex examples.


## [Get Started with Google Tools](https://github.com/portiaAI/portia-agent-examples/edit/main/get_started_google_tools/)

Demonstrates a number of key features of the [Portia SDK](https://github.com/portiaAI/portia-sdk-python) including explicit planning, clarification and authentication. You can read more about the SDK and these concepts in the [Portia SDK documentation](https://docs.portialabs.ai/SDK/portia).

## [AI Research Agent](https://github.com/portiaAI/portia-agent-examples/tree/main/ai-research-agent/)

How to use Portia AI to build an agent that can receive emails about a topic, summarise them to slack and then create a short (2-3 mins) podcast from them. It utilises the [Gmail tools](https://docs.portialabs.ai/gmail-tools) and [Slack tools](https://docs.portialabs.ai/portia-tools/slack/) provided by Portia Cloud to read emails about 'AI' and post the summary to slack, as well as creating a new local [Podcastfy](https://github.com/souzatharsis/podcastfy/tree/main) for podcast creation.

## [Portia SDK Discord Bot](https://github.com/portiaAI/portia-agent-examples/edit/main/discord-knowledge-bot/)

Retrieve Github issues alongside a locally-implemented RAG tool to load and retrieve information from the Portia SDK documentation. For the vector database for our RAG tool, we use [Weaviate](https://weaviate.io/), which is an awesome AI-native vector database - see their quickstart guide [here](https://weaviate.io/developers/weaviate/quickstart).


## [Portia SDK Refund Agent with MCP](https://github.com/portiaAI/portia-agent-examples/tree/main/refund-agent-mcp/)

This example demonstrates how to integrate tools from a Model Context Protocol (MCP) server into the Portia SDK. Here we create an Agent that can handle customer service refund requests using a Stripe integration via their [MCP server](https://github.com/stripe/agent-toolkit/tree/main/modelcontextprotocol).

Alongside MCP integrations, this example also demonstrates how [Clarifications](https://docs.portialabs.ai/understand-clarifications) can be used to keep humans in the loop, protecting against unwanted agent actions such as refunding customers payments incorrectly.

## [Improving Planning with User-Led Learning](https://github.com/portiaAI/portia-agent-examples/tree/main/improving-planning-with-ull/)

This project demonstrates Portia's User-Led Learning (ULL) feature, which allows agents to learn from example plans and improve their planning capabilities over time. Through a series of progressive examples, it shows how providing plan examples can guide the agent to create more effective plans for similar tasks, even when given vague instructions.
