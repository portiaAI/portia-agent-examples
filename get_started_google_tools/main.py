from dotenv import load_dotenv
from portia.runner import Runner
from portia.config import StorageClass, Config
from portia.workflow import WorkflowState
from portia.clarification import MultipleChoiceClarification, InputClarification, ActionClarification
from portia.tool_registry import PortiaToolRegistry

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
- Get my ({user_email}) availability from Google Calendar tomorrow between 10:00 and 17:00 for a 30 minute meeting
- Schedule a meeting with {receipient_email} at a time that works for me with the title "Portia AI Demo" and a description of the meeting as "Test demo".
- Send an email to {receipient_email} with the details of the meeting you scheduled.
'''

print("\nA plan will now be generated. Please wait...")

# Instantiate a Portia runner. Load it with the default config and with Portia cloud tools above
my_config = Config.from_default()
runner = Runner(config=my_config, tools=PortiaToolRegistry(my_config))

# Generate the plan from the user query and print it
plan = runner.generate_plan(task())
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
        plan = runner.generate_plan(task())
        print("\nHere is the updated plan steps:")
        [print(step.model_dump_json(indent=2)) for step in plan.steps]

# Execute the workflow
print("\nThe workflow will now be executed. Please wait...")
workflow = runner.create_workflow(plan)
workflow = runner.execute_workflow(workflow)

while workflow.state == WorkflowState.NEED_CLARIFICATION:
    # If clarifications are needed, resolve them before resuming the workflow
    print("\nPlease resolve the following clarifications to continue")
    for clarification in workflow.get_outstanding_clarifications():
        # Usual handling of Input and Multiple Choice clarifications
        if isinstance(clarification, (InputClarification, MultipleChoiceClarification)):
            print(f"{clarification.user_guidance}")
            user_input = input("Please enter a value:\n" +
                               (clarification.choices
                                if isinstance(clarification, MultipleChoiceClarification)
                                else ""))
            workflow = runner.resolve_clarification(clarification, user_input, workflow)
        
        # Handling of Action clarifications
        if isinstance(clarification, ActionClarification):
            print(f"{clarification.user_guidance} -- Please click on the link below to proceed.")
            print(clarification.action_url)
            workflow = runner.wait_for_ready(workflow)

    # Once clarifications are resolved, resume the workflow
    workflow = runner.execute_workflow(workflow)

# Serialise into JSON and print the output
print(f"{workflow.model_dump_json(indent=2)}")