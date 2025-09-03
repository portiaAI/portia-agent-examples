"""
PlanBuilderV2 Example - Gold Purchase with Receipt Generation

This example demonstrates how to use PlanBuilderV2 to create a plan for purchasing gold
and generating a receipt. PlanBuilderV2 offers methods to create each part of the plan iteratively:

- .input() adds input parameters to the plan
- .invoke_tool_step() adds a step that directly invokes a tool
- .user_input() collects user input during plan execution
- .function_step() calls a Python function to perform calculations
- .user_verify() asks for user confirmation before proceeding
- .if_(), .else_(), .endif() add conditional branching to the plan
- .llm_step() uses the LLM to generate content (receipt in this case)
- .single_tool_agent_step() uses an agent to handle tool interactions
- .final_output() defines the final output schema
"""

from dotenv import load_dotenv
from pydantic import BaseModel

from portia import Input, PlanBuilderV2, Portia, StepOutput
from portia.cli import CLIExecutionHooks

load_dotenv()


class CommodityPriceWithCurrency(BaseModel):
    """Price of a commodity."""

    price: float
    currency: str


class FinalOutput(BaseModel):
    """Final output of the plan."""

    receipt: str
    email_address: str


portia = Portia(execution_hooks=CLIExecutionHooks())

# Create a plan using PlanBuilderV2
# This demonstrates the declarative approach to building plans
plan = (
    PlanBuilderV2("Buy some gold")
    # Step 1: Add input parameter for currency
    .input(name="currency", description="The currency to purchase the gold in", default_value="GBP")
    # Step 2: Search for current gold price using the search tool
    .invoke_tool_step(
        step_name="Search gold price",
        tool="search_tool",
        args={
            "search_query": f"What is the price of gold per ounce in {Input('currency')}?",
        },
        output_schema=CommodityPriceWithCurrency,
    )
    # Step 3: Collect user input for purchase quantity
    .user_input(
        message="How many ounces of gold do you want to purchase?",
        options=[50, 100, 200],
    )
    # Step 4: Calculate total price using a Python function
    .function_step(
        step_name="Calculate total price",
        function=lambda price_with_currency, purchase_quantity: (
            price_with_currency.price * purchase_quantity
        ),
        args={
            "price_with_currency": StepOutput("Search gold price"),
            "purchase_quantity": StepOutput(1),
        },
    )
    # Step 5: Ask for user verification before proceeding
    .user_verify(
        message=(
            f"Do you want to proceed with the purchase? Price is "
            f"{StepOutput('Calculate total price')}"
        )
    )
    # Step 6: Conditional branching based on total price
    .if_(
        condition=lambda total_price: total_price > 100,  # noqa: PLR2004
        args={"total_price": StepOutput("Calculate total price")},
    )
    .function_step(function=lambda: print("Hey big spender!"))  # noqa: T201
    .else_()
    .function_step(function=lambda: print("We need more gold!"))  # noqa: T201
    .endif()
    # Step 7: Generate receipt using LLM
    .llm_step(
        task="Create a fake receipt for the purchase of gold.",
        inputs=[StepOutput("Calculate total price"), Input("currency")],
    )
    # Step 8: Send the receipt via email using single tool agent step
    .single_tool_agent_step(
        task="Send the receipt to Robbie in an email at not_an_email@portialabs.ai",
        tool="portia:google:gmail:send_email",
        inputs=[StepOutput(9)],
    )
    # Step 9: Define the final output schema
    .final_output(
        output_schema=FinalOutput,
    )
    .build()
)

if __name__ == "__main__":
    print("PlanBuilderV2 Example - Gold Purchase with Receipt Generation")
    print("=" * 60)
    
    # Print the plan structure
    print("\nPlan Structure:")
    print(plan.pretty_print())
    
    # Run the plan with sample inputs
    print("\nExecuting plan...")
    plan_run = portia.run_plan(
        plan, 
        plan_run_inputs={
            "currency": "USD"
        }
    )
    
    print(f"\nPlan execution completed with state: {plan_run.state}")
    
    if plan_run.outputs.final_output:
        final_output = plan_run.outputs.final_output.get_value()
        print(f"\nFinal Output:")
        print(f"Receipt: {final_output.receipt}")
        print(f"Email Address: {final_output.email_address}")
    
    print("\nStep Outputs:")
    for step_name, output in plan_run.outputs.step_outputs.items():
        if output:
            print(f"  {step_name}: {output.get_value()}")
