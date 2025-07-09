from portia import Portia, Config, DefaultToolRegistry, InMemoryToolRegistry
from portia.cli import CLIExecutionHooks
from portia.open_source_tools.llm_tool import LLMTool
from pydantic import BaseModel, Field
from enum import Enum
from dotenv import load_dotenv

load_dotenv(override=True)

# Define personas participating in the planning poker and load Portia codebase summary to help with estimation
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
    reason: str = Field(..., description="Discuss the reasoning behind the estimate, any issues or assumptions you made, and any other relevant information")

class PlanningPokerEstimateList(BaseModel):
    """A list of planning poker estimates"""
    estimates: list[PlanningPokerEstimate] = Field(..., description="The estimates")

# Initialize Portia
config = Config.from_default()
portia = Portia(
    config=config,
    tools=DefaultToolRegistry(config=config) + InMemoryToolRegistry([estimate_tool]),
    execution_hooks=CLIExecutionHooks(),
)

# Get tickets from Linear and estimate the size of the tickets
project = "Async Portia"
query = f"""Get the tickets i'm working on from Linear with a limit of 3 on the tool call. Then filter specifically for those regarding the {project} project.
    For each combination of the tickets above and the following personas, estimate the size of the ticket.
    {personas}
    
    Return the estimates in a list of PlanningPokerEstimate objects, with estimate sizes averaged across the personas for each ticket.
    """
estimates = portia.run(
    query=query,
    structured_output_schema=PlanningPokerEstimateList,
).outputs.final_output.value.estimates # type: ignore[attr-defined]

# Print the estimates
print(f"\n\n***** Printing {len(estimates)} estimates *****\n")
for estimate in estimates:
    print(f"""Ticket: {estimate.ticket_id} - {estimate.ticket_title} - Estimate: {estimate.size} 
        Reason: {estimate.reason}"""
    )