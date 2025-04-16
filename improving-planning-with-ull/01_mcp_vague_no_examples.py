#!/usr/bin/env python
# coding: utf-8

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
plan = portia_instance.plan(vague_prompt)
print(plan.pretty_print())
