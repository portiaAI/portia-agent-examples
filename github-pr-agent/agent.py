"""
GitHub PR Agent - A Portia agent that analyzes GitHub PRs and provides feedback.

This agent:
1. Reads the latest PR for the portiaAI/platform repo
2. Uses an LLM to create a description for it
3. Uses an LLM to give feedback on the code
4. Comments on the PR
"""

import os
import sys
from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    ExecutionContext,
    LLMModel,
    LogLevel,
    PlanRunState,
    Portia,
    execution_context,
)
from portia.cli import CLIExecutionHooks
from tools import github_pr_tool_registry

# Load environment variables
load_dotenv()

# Check for required environment variables
required_env_vars = ["PORTIA_API_KEY", "OPENAI_API_KEY", "GITHUB_TOKEN"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in a .env file or in your environment.")
    sys.exit(1)

# Configure Portia
config = Config.from_default(
    llm_model_name=LLMModel.GPT_4_O,
    default_log_level=LogLevel.DEBUG,
)

# Combine default tools with our custom GitHub PR tools
tools = DefaultToolRegistry(config) + github_pr_tool_registry

# Instantiate Portia
portia = Portia(
    config=config,
    tools=tools,
    execution_hooks=CLIExecutionHooks(),
)

# Define the repository to analyze
REPO = "portiaAI/platform"

# Define the task for Portia
task = f"""
Analyze the latest PR in the {REPO} GitHub repository by following these steps:
1. Get the latest PR from the {REPO} repository
2. Create a concise but informative description for the PR based on the changes
3. Analyze the code changes and provide constructive feedback, including:
   - Code quality assessment
   - Potential bugs or issues
   - Suggestions for improvements
   - Any security concerns
4. Post a comment on the PR with both the description and feedback
"""

# Execute the agent
with execution_context(
    end_user_id="github-pr-agent",
):
    # Generate the plan
    print("\nGenerating plan...")
    plan = portia.plan(task)
    
    print("\nHere are the steps in the generated plan:")
    [print(step.model_dump_json(indent=2)) for step in plan.steps]
    
    # Ask for confirmation before executing the plan
    if os.getenv("CI") != "true":
        user_input = input("\nAre you happy with the plan? (y/n):\n")
        if user_input.lower() != "y":
            print("Exiting without executing the plan.")
            sys.exit(0)
    
    # Execute the plan
    print("\nExecuting the plan...")
    run = portia.run_plan(plan)
    
    # Check if the plan completed successfully
    if run.state != PlanRunState.COMPLETE:
        print(f"Plan run failed with state {run.state}. Check logs for details.")
        sys.exit(1)
    
    print("\nPlan executed successfully!")
    print(f"Check the {REPO} repository for the PR comment.")