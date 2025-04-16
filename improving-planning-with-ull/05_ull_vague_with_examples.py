#!/usr/bin/env python3

"""
This script shows how to use `get_similar_plans` to obtain relevant example plans from Portia cloud.
You must have run the previous script, `04_ull_create_example_plans.py`,
and have 'liked' the resulting plans in the Portia dashboard before running this script.

This script is part of a set of scripts designed to demonstrate how user-led learning can improve planning results.
"""

from common import init_portia

# Define the prompts for testing
vague_prompt = """
Read the refund request email from the customer and decide if it should be approved or rejected.
If you think the refund request should be approved, check with a human for final approval and then process the refund.

To process the refund, you'll need to find the customer in Stripe and then find their payment intent.

The refund policy can be found in the file: ./refund_policy.txt

The refund request email can be found in "inbox.txt" file
"""

portia_instance = init_portia()
example_plans = portia_instance.storage.get_similar_plans(vague_prompt)
if not example_plans:
    print(
        "No example plans were found in Portia storage. Did you remember to create and 'like' the plans from the previous step?"
    )
else:
    print(f"{len(example_plans)} similar plans were found.")
plan = portia_instance.plan(
    vague_prompt,
    example_plans=example_plans,
)
print(plan.pretty_print())
