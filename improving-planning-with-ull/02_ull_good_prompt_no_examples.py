#!/usr/bin/env python
# coding: utf-8

"""
This script demonstrates how to execute a well-written prompt with Portia.

It is part of a set of scripts designed to demonstrate how user-led learning can improve planning results.
"""


from common import init_portia

good_prompt = """
Read the refund request email from the customer and decide if it should be approved or rejected.
If you think the refund request should be approved, check with a human for final approval and then process the refund.

Stripe instructions -- To create a refund in Stripe, you need to:
* Find the Customer using their email address from the List of Customers in Stripe.
* Find the Payment Intent ID using the Customer from the previous step, from the List of Payment Intents in Stripe.
* Create a refund against the Payment Intent ID.

The refund policy can be found in the file: ./refund_policy.txt

The refund request email can be found in "inbox.txt" file
"""
portia_instance = init_portia()
plan = portia_instance.plan(good_prompt)
print(plan.pretty_print())
