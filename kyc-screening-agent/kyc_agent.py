#!/usr/bin/env python3
import os
import random
from dotenv import load_dotenv
from portia import (
    Config,
    DefaultToolRegistry,
    ExecutionContext,
    InMemoryToolRegistry,
    LLMModel,
    LogLevel,
    PlanRunState,
    Portia,
    Tool,
    execution_context,
)
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field

load_dotenv()

class RiskAssessmentSchema(BaseModel):
    """Input for RiskAssessmentTool."""
    person_name: str = Field(
        ...,
        description=("The full name of the person to assess for risk."),
    )

class RiskAssessmentTool(Tool[int]):
    """Calculate a risk factor for a person based on their name."""

    id: str = "risk_assessment_tool"
    name: str = "Risk Assessment Tool"
    description: str = (
        "Used to calculate a risk factor (0-10) for a person based on their name. "
        "This is a dummy tool that returns a random number for demonstration purposes."
    )
    args_schema: type[BaseModel] = RiskAssessmentSchema
    output_schema: tuple[str, str] = (
        "int",
        "A risk factor score from 0 (lowest risk) to 10 (highest risk).",
    )

    def run(self, _: ExecutionContext, person_name: str) -> int:
        """Run the Risk Assessment Tool."""
        # This is a dummy implementation that returns a random risk factor
        # In a real implementation, this would call an actual risk assessment API
        risk_factor = random.randint(0, 10)
        print(f"Risk factor for {person_name}: {risk_factor}/10")
        return risk_factor

def main():
    print("KYC Screening Agent")
    print("===================")
    print("This agent performs Know Your Customer (KYC) screening by:")
    print("1. Searching the web for information about the person")
    print("2. Analyzing search results for potential illegal activities")
    print("3. Calculating a risk factor")
    print("4. Making a KYC assessment based on the findings")
    print()
    
    person_name = input("Please enter the full name of the person to screen: ")
    
    # Configure Portia
    config = Config.from_default(
        llm_model_name=LLMModel.GPT_4_O,
        default_log_level=LogLevel.DEBUG,
    )
    
    # Set up tools registry with our custom risk assessment tool
    tools = DefaultToolRegistry(config) + InMemoryToolRegistry.from_local_tools(
        [RiskAssessmentTool()]
    )
    
    # Instantiate Portia with our configuration and tools
    portia = Portia(
        config=config,
        tools=tools,
        execution_hooks=CLIExecutionHooks(),
    )
    
    # Define the KYC screening task
    task = f"""
    Perform a KYC (Know Your Customer) screening for {person_name} by following these steps:
    
    1. Use a web search to find information about {person_name}. Search for at least 3 relevant pages.
    2. For each search result, analyze the content to determine if there is any evidence of illegal activity.
    3. Rate each page on this scale: 'definitely, maybe, possibly, unlikely, definitely not' regarding involvement in illegal activity.
    4. Use the Risk Assessment Tool to get a risk factor score for {person_name}.
    5. Based on the web search analysis and risk factor score, make a final assessment on whether {person_name} passes the KYC check.
       - If the risk factor is 8-10 OR if any page is rated as 'definitely' involved in illegal activity, the person fails the KYC check.
       - If the risk factor is 5-7 OR if any page is rated as 'maybe' involved in illegal activity, the person is flagged for further review.
       - Otherwise, the person passes the KYC check.
    6. Provide a detailed report with your findings and final assessment.
    """
    
    print("\nGenerating KYC screening plan. Please wait...")
    
    with execution_context(end_user_id="kyc-screening-agent"):
        # Generate the plan
        plan = portia.plan(task)
        print("\nHere are the steps in the generated KYC screening plan:")
        [print(step.model_dump_json(indent=2)) for step in plan.steps]
        
        # Ask user if they're happy with the plan
        user_input = input("\nAre you happy with the plan? (y/n): ")
        if user_input.lower() != "y":
            print("Exiting without executing the plan.")
            return
        
        print("\nExecuting KYC screening plan. This may take a few minutes...")
        run = portia.run_plan(plan)
        
        if run.state != PlanRunState.COMPLETE:
            print(f"Plan execution failed with state {run.state}. Check logs for details.")
        else:
            print("\nKYC screening completed successfully.")
            print("\nFinal KYC Assessment Report:")
            print("============================")
            # The final output is in the run outputs
            if run.outputs.final_output:
                print(run.outputs.final_output)
            else:
                print("No final assessment available.")

if __name__ == "__main__":
    main()