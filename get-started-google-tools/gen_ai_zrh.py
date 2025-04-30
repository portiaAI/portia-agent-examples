from dotenv import load_dotenv
from portia import Config, Portia, PortiaToolRegistry, StorageClass
from portia.cli import CLIExecutionHooks

load_dotenv()

task = (
"""Please help me accomplish the following tasks:
Tasks:
- Get my (emma@portialabs.ai) availability from Google Calendar tomorrow between 10:00 and 17:00
- Schedule a 30 minute meeting with demo@portialabs.ai at a time that works for me with the title
"Portia AI Demo" and a description of the meeting as "Test demo".
- Send an email to demo@portialabs.ai with the details of the meeting you scheduled.
"""
)

print("\nA plan will now be generated. Please wait...")

# Instantiate a Portia runner. Load it with the default config and with Portia cloud tools above.
# Use the CLIExecutionHooks to allow the user to handle any clarifications at the CLI.
my_config = Config.from_default(storage_class=StorageClass.CLOUD)
portia = Portia(
    config=my_config,
    tools=PortiaToolRegistry(my_config),
    execution_hooks=CLIExecutionHooks(),
)

# Generate the plan from the user query and print it
plan = portia.plan(task())
input("Press Enter to continue...")
plan_run = portia.run_plan(plan)

# Serialise into JSON and print the output
print(f"{plan_run.model_dump_json(indent=2)}")
