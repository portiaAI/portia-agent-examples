# ruff: noqa
from portia import Config, Portia, example_tool_registry
from dotenv import load_dotenv

load_dotenv(override=True)

task = """Find a city in the Northern Hemisphere and output the weather in that city right now."""

# Instantiate a Portia runner. Load it with the open source tool registry.
portia = Portia(config=Config.from_default(), tools=example_tool_registry)

plan = portia.plan(task)
print(plan.pretty_print())
