#!/usr/bin/env python3

"""
This script demonstrates how to manually construct an example plan and provide it to Portia.

It is part of a set of scripts designed to demonstrate how user-led learning can improve planning results.
"""


from portia.plan import PlanBuilder

from common import init_portia

# Example 1: Create refund given user email
plan1 = (
    PlanBuilder(
        "Create a refund for a customer with email john.doe@example.com"
    )
    .step(
        "Find the customer in Stripe by email john.doe@example.com",
        "mcp:stripe:list_customers",
        "$customer_data",
    )
    .step(
        "Extract customer ID from response",
        "extract_customer_id_tool",
        "$customer_id",
    )
    .input("$customer_data")
    .step(
        "Find payment intents for the customer",
        "mcp:stripe:list_payment_intents",
        "$payment_intents",
    )
    .input("$customer_id")
    .step(
        "Extract payment intent ID from response",
        "extract_payment_intent_id_tool",
        "$payment_intent_id",
    )
    .input("$payment_intents")
    .step("Create the refund", "mcp:stripe:create_refund", "$refund_result")
    .input("$payment_intent_id")
    .build()
)

vague_prompt = """
Read the refund request email from the customer and decide if it should be approved or rejected.
If you think the refund request should be approved, check with a human for final approval and then process the refund.

To process the refund, you'll need to find the customer in Stripe and then find their payment intent.

The refund policy can be found in the file: ./refund_policy.txt

The refund request email can be found in "inbox.txt" file
"""

portia_instance = init_portia()

plan = portia_instance.plan(
    vague_prompt,
    example_plans=[plan1],
)

print(plan.pretty_print())
