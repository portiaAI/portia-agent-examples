from dotenv import load_dotenv
from portia import Config, Portia, PortiaToolRegistry
from portia.cli import CLIExecutionHooks

load_dotenv(override=True)

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
- If I am available, schedule a 30 minute meeting with {receipient_email} at a time that works for me with the title "Portia AI Demo" and a description of the meeting as "Test demo".
- and send an email to {receipient_email} with the details of the meeting you scheduled.
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

# Generate the plan from the user query and print it
plan = portia.plan(task())
print("\nHere are the steps in the generated plan:")
[print(step.model_dump_json(indent=2)) for step in plan.steps]

# Iterate on the plan with the user until they are happy with it
ready_to_proceed = False
while not ready_to_proceed:
    user_input = input("Are you happy with the plan? (y/n):\n")
    if user_input == "y":
        ready_to_proceed = True
    else:
        user_input = input("Any additional guidance for the planner?:\n")
        constraints.append(user_input)
        plan = portia.plan(task())
        print("\nHere are the updated steps in the plan:")
        [print(step.model_dump_json(indent=2)) for step in plan.steps]

# Execute the plan
print("\nThe plan will now be executed. Please wait...")
plan_run = portia.run_plan(plan)

# Serialise into JSON and print the output
print(f"{plan_run.model_dump_json(indent=2)}")
