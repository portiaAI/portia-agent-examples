from enum import Enum
from typing import List

from dotenv import load_dotenv
from portia import Config, DefaultToolRegistry, InMemoryToolRegistry, Plan, PlanBuilderV2, Portia, StepOutput
from portia.cli import CLIExecutionHooks
from portia.open_source_tools.llm_tool import LLMTool
from pydantic import BaseModel, Field

load_dotenv(override=True)

PERSONAS = [
    "You are a frontend developer, assess the ticket and estimate with your relevant experience",
    "You are a backend developer, assess the ticket and estimate with your relevant experience", 
    "You are a devops engineer, assess the ticket and estimate with your relevant experience",
]

try:
    with open("./context.md", "r") as f:
        codebase_context = f.read()
except FileNotFoundError:
    codebase_context = """
    Portia is a Python framework for formalized planning and execution of agentic LLM workflows.
    It supports robust, inspectable, and interactive agentic systems with explicit plans and stepwise execution.
    """

tool_context = f"Conform to the nearest sizing value, rounding up to the nearest day. If the ticket is too large to estimate, return TLTE.\n\n{codebase_context}"

estimate_tool = LLMTool(
    id='ticket_estimator_tool',
    name='Ticket Estimator', 
    tool_context=tool_context,
)

class Sizing(Enum):
    """The size of the planning poker estimate"""
    ONE_DAY = "1D"
    THREE_DAYS = "3D"
    FIVE_DAYS = "5D"
    SEVEN_DAYS = "7D"
    TEN_DAYS = "10D"
    TOO_LARGE_TO_ESTIMATE = "TLTE"

class PlanningPokerEstimate(BaseModel):
    """A planning poker card estimate"""
    ticket_id: str = Field(..., description="The id of the ticket in Linear")
    ticket_title: str = Field(..., description="The title of the ticket")
    size: Sizing = Field(..., description="The size of the planning poker card")
    reason: str = Field(..., description="Discuss the reasoning behind the estimate, any issues or assumptions you made, and any other relevant information")

class PlanningPokerEstimateList(BaseModel):
    """A list of planning poker estimates"""
    estimates: List[PlanningPokerEstimate] = Field(..., description="The estimates")

class LinearTickets(BaseModel):
    """Linear tickets filtered for the specified project"""
    tickets: List[dict] = Field(..., description="List of tickets from Linear for the project")

class PersonaEstimates(BaseModel):
    """Estimates from different personas for tickets"""
    estimates: List[dict] = Field(..., description="Raw estimates from each persona for each ticket")

def create_planning_poker_plan(project: str = "Async Portia") -> Plan:
    """
    Create a declarative plan for planning poker estimation using PlanBuilderV2.
    
    Args:
        project: The project name to filter tickets for
        
    Returns:
        A Plan object ready for execution
    """
    plan = (
        PlanBuilderV2("Planning Poker Estimation")
        
        .input(
            name="project",
            description="The project name to filter Linear tickets for",
            default_value=project
        )
        
        .llm_step(
            step_name="get_linear_tickets",
            task="Get the tickets I'm working on from Linear with a limit of 3. Use any available tools to access Linear and retrieve my current tickets."
        )
        
        .llm_step(
            step_name="filter_project_tickets",
            task="Filter the Linear tickets for those specifically regarding the {project} project. Return only tickets that match this project.",
            inputs=[StepOutput("get_linear_tickets")],
            output_schema=LinearTickets
        )
        
        .llm_step(
            step_name="generate_persona_estimates",
            task=f"""For each ticket and each of the following personas, estimate the size of the ticket:
            
            Personas:
            {chr(10).join(f'- {persona}' for persona in PERSONAS)}
            
            For each combination of ticket and persona, provide an estimate using the ticket_estimator_tool.
            Return all estimates with ticket information and persona details.""",
            inputs=[StepOutput("filter_project_tickets")],
            output_schema=PersonaEstimates
        )
        
        .llm_step(
            step_name="aggregate_estimates",
            task="""Take the estimates from all personas for each ticket and calculate the average estimate size for each ticket.
            
            For sizing, use these values in order: 1D, 3D, 5D, 7D, 10D, TLTE
            When averaging, round up to the nearest sizing value.
            
            Return a list of PlanningPokerEstimate objects with the averaged estimates for each ticket.""",
            inputs=[StepOutput("generate_persona_estimates"), StepOutput("filter_project_tickets")],
            output_schema=PlanningPokerEstimateList
        )
        
        .final_output(output_schema=PlanningPokerEstimateList)
        
        .build()
    )
    
    return plan

def run_planning_poker(project: str = "Async Portia") -> PlanningPokerEstimateList:
    """
    Run the planning poker estimation agent.
    
    Args:
        project: The project name to filter tickets for
        
    Returns:
        PlanningPokerEstimateList with estimates for all tickets
    """
    config = Config.from_default()
    portia = Portia(
        config=config,
        tools=DefaultToolRegistry(config=config) + InMemoryToolRegistry([estimate_tool]),
        execution_hooks=CLIExecutionHooks(),
    )
    
    plan = create_planning_poker_plan(project)
    
    print("\nHere are the steps in the generated plan:")
    print(plan.pretty_print())
    
    plan_run = portia.run_plan(
        plan,
        plan_run_inputs={"project": project},
        structured_output_schema=PlanningPokerEstimateList,
    )
    
    if plan_run.outputs.final_output:
        estimates = plan_run.outputs.final_output.get_value()
        return estimates
    else:
        raise RuntimeError("Plan execution failed - no final output generated")

def main():
    """Main entry point for the planning poker agent."""
    project = "Async Portia"
    
    print(f"Running Planning Poker estimation for project: {project}")
    print("=" * 60)
    
    try:
        result = run_planning_poker(project)
        
        print(f"\n\n***** Printing {len(result.estimates)} estimates *****\n")
        for estimate in result.estimates:
            print(f"""Ticket: {estimate.ticket_id} - {estimate.ticket_title} - Estimate: {estimate.size.value}
        Reason: {estimate.reason}""")
            
    except Exception as e:
        print(f"Error running planning poker estimation: {e}")
        raise

if __name__ == "__main__":
    main()
