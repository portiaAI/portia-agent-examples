from dotenv import load_dotenv
from portia import Config, Portia, PortiaToolRegistry, execution_context
from portia.cli import CLIExecutionHooks

load_dotenv()

outline = """
This demo requires you to have a Google Calendar and GMail account, and the email address of someone you want to schedule a meeting with.
"""

print(outline)
user_email = input("Please enter your email address:\n")
receipient_email = input(
    "Please enter the email address of the person you want to schedule a meeting with:\n"
)

constraints = []

task = (
    lambda: f"""
Please help me accomplish the following tasks, ensuring you take into account the following constraints: {"".join(constraints)}
Tasks:
- Get my ({user_email}) availability from Google Calendar tomorrow between 10:00 and 17:00
- Schedule a 30 minute meeting with {receipient_email} at a time that works for me with the title "Portia AI Demo" and a description of the meeting as "Test demo".
- Send an email to {receipient_email} with the details of the meeting you scheduled.
"""
)

print("\nA plan will now be generated. Please wait...")

# Instantiate a Portia runner. Load it with the default config and with Portia cloud tools above.
# Use the CLIExecutionHooks to allow the user to handle any clarifications at the CLI.
my_config = Config.from_default()
portia = Portia(
    config=my_config,
    tools=PortiaToolRegistry(my_config),
    execution_hooks=CLIExecutionHooks(),
)

with execution_context(end_user_id="Mr james bond"):
    # Generate the plan from the user query and print it
    plan_run = portia.run(task())

# Serialise into JSON and print the output
print(f"{plan_run.model_dump_json(indent=2)}")
