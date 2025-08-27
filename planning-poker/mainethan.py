"""Simple Example."""

import asyncio
from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from portia import Config, LogLevel
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input, StepOutput
from portia.cli import CLIExecutionHooks
from portia.open_source_tools.llm_tool import LLMTool
from portia.portia import Portia
from portia.tool_registry import DefaultToolRegistry, InMemoryToolRegistry


load_dotenv(override=True)

# Define personas of in the planning poker and load Portia codebase summary to help with estimation
personas = [
    "You are a frontend developer, assess the ticket and estimate with your relevant experience",
    "You are a backend developer, assess the ticket and estimate with your relevant experience",
    "You are a devops engineer, assess the ticket and estimate with your relevant experience",
]

with open("./context.md", "r") as f:
    codebase_context = f.read()
tool_context = f"Conform to the nearest sizing value, rounding up to the nearest day. If the ticket is too large to estimate, return TLTE.\n\n{codebase_context}"

estimate_tool = LLMTool(
    id='ticket_estimator_tool',
    name='Ticket Estimator',
    tool_context=tool_context,
)

# Define output schema for Linear tickets and the planning poker estimates
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
    persona: str = Field(..., description="The persona that made the estimate")
    reason: str = Field(..., description="Discuss the reasoning behind the estimate, any issues or assumptions you made, and any other relevant information")

class PlanningPokerEstimateList(BaseModel):
    """A list of planning poker estimates"""
    estimates: list[PlanningPokerEstimate] = Field(..., description="The estimates")

class LinearTicket(BaseModel):
    """A linear ticket"""
    title: str = Field(..., description="The title of the ticket")
    description: str = Field(..., description="The description of the ticket")
    ticket_id: str = Field(..., description="The id of the ticket")

class LinearTicketList(BaseModel):
    """A list of linear tickets"""
    tickets: list[LinearTicket] = Field(..., description="The tickets")


config = Config.from_default(default_log_level=LogLevel.DEBUG)
portia = Portia(
    config=config,
    tools=DefaultToolRegistry(config=config) + InMemoryToolRegistry([estimate_tool]),
    execution_hooks=CLIExecutionHooks(),
)

project = "Async Portia"
query = f"""Get the tickets i'm working on from Linear with a limit of 3 on the tool call. \
    Then filter specifically for those regarding the specified project. \
    For each combination of the tickets above and the following personas, \
    estimate the size of the ticket.
    {personas}

    Return the estimates in a list of PlanningPokerEstimate objects, with estimate sizes averaged across the personas for each ticket.
    """

plan = (
    PlanBuilderV2(query)
    .input(name="project", description="The Linear project to filter tickets for")
    .single_tool_agent_step(
        step_name="get_linear_tickets",
        tool="portia:mcp:mcp.linear.app:list_my_issues",
        task="Get all my Linear tickets - limit yourself to 20.",
        output_schema=LinearTicketList,
    )
    .llm_step(
        step_name="filter_linear_tickets",
        task="Filter the tickets to only include those regarding the project.",
        inputs=[StepOutput("get_linear_tickets"), Input("project")],
        output_schema=LinearTicketList,
    )
    .build()
)

my_project_tickets = asyncio.run(portia.arun_plan(plan, plan_run_inputs={"project": project}))
print(my_project_tickets.model_dump_json(indent=2))

print(f"\n\n***** Estimating the tickets *****\n\n")
estimates = []

tickets_output = my_project_tickets.outputs.final_output.get_value()

for ticket in tickets_output.tickets:
    print(f"Estimating ticket: {ticket.title}")
    estimate_plan = (
        PlanBuilderV2(f"Estimate the size of the ticket for each of the personas")
            .input(name="ticket", description="the linear ticket to estimate effort for")
            .input(name="personas", description="the developers estimating the ticket effort.")
            .single_tool_agent_step(
                task=f"Estimate the size of the ticket in the inputs for each persona.", 
                inputs=[Input("ticket"), Input("personas")],
                tool="ticket_estimator_tool",
                output_schema=PlanningPokerEstimateList,
            )
            .final_output(
                output_schema=PlanningPokerEstimateList,
            )
            .build()
    )

    result = portia.run_plan(
        estimate_plan, 
        plan_run_inputs={"ticket": ticket, "personas": personas},
    )
    estimates.append(result)

print(estimates)