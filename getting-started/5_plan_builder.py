"""
PlanBuilderV2 Example - Declarative Plan Building

This example demonstrates how to use PlanBuilderV2 to create plans declaratively.
PlanBuilderV2 offers methods to create each part of the plan iteratively:

- .llm_step() adds a step that sends a query to the underlying LLM
- .invoke_tool_step() adds a step that directly invokes a tool. Requires mapping of step outputs to tool arguments.
- .single_tool_agent_step() is similar to .invoke_tool_step() but an LLM call is made to map the inputs to the step to what the tool requires creating flexibility.
- .function_step() is identical to .invoke_tool_step() but calls a Python function rather than a tool with an ID.
- .if_(), .else_if_(), .else_() and .endif() are used to add conditional branching to the plan.

Required configuration:
- `PORTIA_API_KEY`
- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`)
- `TAVILY_API_KEY` (for search functionality)
"""

from dotenv import load_dotenv
from pydantic import BaseModel

from portia import (
    Config,
    DefaultToolRegistry,
    Input,
    PlanBuilderV2,
    Portia,
    StepOutput,
    StorageClass,
)
from portia.cli import CLIExecutionHooks

load_dotenv()


class CommodityPriceWithCurrency(BaseModel):
    """Price of a commodity with currency information."""
    
    price: float
    currency: str


class TotalCostResult(BaseModel):
    """Result of total cost calculation."""
    
    total_cost: float
    currency: str


class FinalOutput(BaseModel):
    """Final output of the plan."""
    
    poem: str
    total_cost: float
    currency: str


# Initialize Portia with default configuration and CLI execution hooks
config = Config.from_default(storage_class=StorageClass.CLOUD)
portia = Portia(
    config=config,
    tools=DefaultToolRegistry(config),
    execution_hooks=CLIExecutionHooks(),
)

# Create a plan using PlanBuilderV2
# This demonstrates the declarative approach to building plans
plan = (
    PlanBuilderV2("Write a poem about the price of gold")
    .input(
        name="purchase_quantity", 
        description="The quantity of gold to purchase in ounces",
        default_value=10
    )
    .input(
        name="currency", 
        description="The currency to purchase the gold in", 
        default_value="GBP"
    )
    # Step 1: Search for current gold price using the search tool
    .invoke_tool_step(
        step_name="Search gold price",
        tool="search_tool",
        args={
            "search_query": f"What is the price of gold per ounce in {Input('currency')}?",
        },
        output_schema=CommodityPriceWithCurrency,
    )
    # Step 2: Calculate total cost using a Python function
    .function_step(
        function=lambda price_with_currency, purchase_quantity: TotalCostResult(
            total_cost=float(price_with_currency.price) * float(purchase_quantity),
            currency=price_with_currency.currency
        ),
        args={
            "price_with_currency": StepOutput("Search gold price"),
            "purchase_quantity": Input("purchase_quantity"),
        },
        step_name="Calculate total cost",
        output_schema=TotalCostResult,
    )
    # Step 3: Write a poem about the current price of gold using LLM
    .llm_step(
        task="Write a poem about the current price of gold",
        inputs=[StepOutput("Calculate total cost"), Input("currency")],
        step_name="Write gold poem",
    )
    # Step 4: Send the poem via email using single tool agent step
    .single_tool_agent_step(
        task="Send the poem to Robbie in an email at donotemail@portialabs.ai",
        tool="portia:google:gmail:send_email",
        inputs=[StepOutput("Write gold poem")],
        step_name="Send email",
    )
    # Step 5: Create final output combining poem and cost information
    .function_step(
        function=lambda poem, cost_result: FinalOutput(
            poem=poem,
            total_cost=cost_result.total_cost,
            currency=cost_result.currency
        ),
        args={
            "poem": StepOutput("Write gold poem"),
            "cost_result": StepOutput("Calculate total cost"),
        },
        step_name="Create final output",
        output_schema=FinalOutput,
    )
    # Define the final output schema
    .final_output(
        output_schema=FinalOutput,
    )
    .build()
)

if __name__ == "__main__":
    print("PlanBuilderV2 Example - Gold Price Poem")
    print("=" * 50)
    
    # Print the plan structure
    print("\nPlan Structure:")
    print(plan.pretty_print())
    
    # Run the plan with sample inputs
    print("\nExecuting plan...")
    plan_run = portia.run_plan(
        plan, 
        plan_run_inputs={
            "purchase_quantity": 5,
            "currency": "USD"
        }
    )
    
    print(f"\nPlan execution completed with state: {plan_run.state}")
    
    if plan_run.outputs.final_output:
        final_output = plan_run.outputs.final_output.get_value()
        print(f"\nFinal Output:")
        print(f"Poem: {final_output.poem}")
        print(f"Total Cost: {final_output.total_cost} {final_output.currency}")
    
    print("\nStep Outputs:")
    for step_name, output in plan_run.outputs.step_outputs.items():
        if output:
            print(f"  {step_name}: {output.get_value()}")
