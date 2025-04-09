from dotenv import load_dotenv
from portia import Config, Portia, PortiaToolRegistry
from portia.cli import CLIExecutionHooks


def main():
    config = Config.from_default(
        default_log_level="DEBUG",
        default_model="ollama/qwen2.5:14b",
    )
    tools = PortiaToolRegistry(config).filter_tools(lambda tool: "github" in tool.id)

    portia = Portia(config=config, execution_hooks=CLIExecutionHooks(), tools=tools)
    plan = portia.plan(
        "Find a Github repository by the organization portiaAI and star it",
        example_plans=[],
    )
    print(plan.pretty_print())
    portia.run_plan(plan)


if __name__ == "__main__":
    load_dotenv()
    main()
