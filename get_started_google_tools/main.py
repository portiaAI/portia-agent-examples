from dotenv import load_dotenv
from portia.config import StorageClass, Config
from portia.plan_run import PlanRunState
from portia.clarification import MultipleChoiceClarification, InputClarification, ActionClarification
from portia.tool_registry import PortiaToolRegistry
from portia import Portia
load_dotenv()

outline = """
This demo requires you to have a Google Calendar and GMail account, and the email address of someone you want to schedule a meeting with.
"""

print(outline)
user_email = input("Please enter your email address:\n")
receipient_email = input("Please enter the email address of the person you want to schedule a meeting with:\n")

constraints = []

task = lambda: f'''
Please help me accomplish the following tasks, ensuring you take into account the following constraints: {"".join(constraints)}
Tasks:
- Get my ({user_email}) availability from Google Calendar tomorrow between 10:00 and 17:00
- Schedule a 30 minute meeting with {receipient_email} at a time that works for me with the title "Portia AI Demo" and a description of the meeting as "Test demo".
- Send an email to {receipient_email} with the details of the meeting you scheduled.
'''

print("\nA plan will now be generated. Please wait...")

# Instantiate a Portia runner. Load it with the default config and with Portia cloud tools above
my_config = Config.from_default()
portia = Portia(config=my_config, tools=PortiaToolRegistry(my_config))

# Generate the plan from the user query and print it
plan = portia.plan(task())
print("\nHere is the plan steps:")
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
        print("\nHere is the updated plan steps:")
        [print(step.model_dump_json(indent=2)) for step in plan.steps]

# Execute the plan run
print("\nThe plan run will now be executed. Please wait...")
plan_run = portia.run_plan(plan)

while plan_run.state == PlanRunState.NEED_CLARIFICATION:
    # If clarifications are needed, resolve them before resuming the workflow
    print("\nPlease resolve the following clarifications to continue")
    for clarification in plan_run.get_outstanding_clarifications():
        # Usual handling of Input and Multiple Choice clarifications
        if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
            print(f"{clarification.user_guidance}")
            user_input = input("Please enter a value:\n" +
                               (str(clarification.options)
                                if isinstance(clarification, MultipleChoiceClarification)
                                else ""))
            plan_run = portia.resolve_clarification(clarification, user_input, plan_run)
        
        # Handling of Action clarifications
        if isinstance(clarification, ActionClarification):
            print(f"{clarification.user_guidance} -- Please click on the link below to proceed.")
            print(clarification.action_url)
            plan_run = portia.wait_for_ready(plan_run)

    # Once clarifications are resolved, resume the workflow
    plan_run = portia.resume(plan_run)

# Serialise into JSON and print the output
print(f"{plan_run.model_dump_json(indent=2)}")