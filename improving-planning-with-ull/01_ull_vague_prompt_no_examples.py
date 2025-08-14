#!/usr/bin/env python3

"""
This script demonstrates how to execute a (not very well-written) prompt with Portia.

It is part of a set of scripts designed to demonstrate how user-led learning can improve planning results.
"""

from common import init_portia

# Define the prompt for testing
vague_prompt = """
Read the refund request email from the customer and decide if it should be approved or rejected.
If you think the refund request should be approved, check with a human for final approval and then process the refund.

To process the refund, you'll need to find the customer in Stripe and then find their payment intent.

The refund policy can be found in the file: ./refund_policy.txt

The refund request email can be found in "inbox.txt" file
"""

# This is function initializes Portia and all the tools.
# You can find it in common.py
portia_instance = init_portia()

# Generate a plan and print it out:
plan = portia_instance.plan(vague_prompt)
print(plan.pretty_print())
