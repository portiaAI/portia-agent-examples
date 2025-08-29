# Portia SDK Getting Started Guide

This directory contains example scripts demonstrating various capabilities of the Portia SDK.

## Getting Started

1. Set up your environment variables (copy `.env.example` to `.env` and add any necessary config values for running each script.)
2. Run any of the examples using `uv run` as shown below

For more information about the Portia SDK, visit the [Portia SDK documentation](https://docs.portialabs.ai).

## Examples

### 1. GitHub OAuth Integration

[1_github_oauth.py](./1_github_oauth.py) - Demonstrates how to use Portia with GitHub OAuth authentication. This example shows how to star a GitHub repository and check Google Calendar availability to schedule meetings.

```bash
uv run 1_github_oauth.py
```

### 2. Tools & End Users

[2_tools_end_users_llms.py](./2_tools_end_users_llms.py) - Shows how to use Portia with various tools for end users and LLMs. This example includes tasks like researching gold prices and fetching weather data to send via email.

```bash
uv run 2_tools_end_users_llms.py
```

### 3. MCP (Model Context Protocol)

[3_mcp.py](./3_mcp.py) - Demonstrates how to use Portia with the Model Context Protocol. This example shows how to read website content using an MCP tool.

```bash
uv run 3_mcp.py
```

### 4. Browser Automation

[4_browser_use.py](./4_browser_use.py) - Shows how to use Portia for browser automation. This example demonstrates finding LinkedIn connections using both local and Browserbase options.

```bash
uv run 4_browser_use.py
```

### 5. PlanBuilderV2 - Declarative Plan Building

[5_plan_builder.py](./5_plan_builder.py) - Demonstrates how to use PlanBuilderV2 to create plans declaratively. This example shows how to build a plan that searches for gold prices, calculates costs, writes poems, and sends emails.

```bash
uv run 5_plan_builder.py
```
