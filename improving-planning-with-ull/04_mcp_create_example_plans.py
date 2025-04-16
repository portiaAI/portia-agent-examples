from portia.plan import PlanBuilder

from common import init_portia

# Create example plans for refund processing
example_plans = []

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
example_plans.append(plan1)

# Example 2: Use file reader to extract email details and then create refund
plan2 = (
    PlanBuilder("Process a refund request from the email in inbox.txt")
    .step(
        "Read the email from inbox.txt", "file_reader_tool", "$email_content"
    )
    .step(
        "Extract customer email from the email content",
        "extract_email_tool",
        "$customer_email",
    )
    .input("$email_content")
    .step(
        "Find the customer in Stripe",
        "mcp:stripe:list_customers",
        "$customer_data",
    )
    .input("$customer_email")
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
example_plans.append(plan2)

# Example 3: Get email details from a 'resolve_user_email_tool' and then create refund
plan3 = (
    PlanBuilder(
        "Process a refund for a customer identified by their order number ORD-12345"
    )
    .step(
        "Resolve the customer email from the order number: ORD-12345",
        "resolve_user_email_from_order_number_tool",
        "$customer_email",
    )
    .step(
        "Find the customer in Stripe",
        "mcp:stripe:list_customers",
        "$customer_data",
    )
    .input("$customer_email")
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
example_plans.append(plan3)

portia = init_portia()
for plan in example_plans:
    portia.storage.save_plan(plan)
print("""
Plans saved in Portia cloud storage.
      
Now you should go to the Portia dashboard and 'like' them.""")
