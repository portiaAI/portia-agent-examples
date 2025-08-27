"""Simple Example."""

import argparse
from enum import Enum

from dotenv import load_dotenv
from portia import Config
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import StepOutput
from portia.cli import CLIExecutionHooks
from portia.portia import Portia
from portia.tool_registry import DefaultToolRegistry
from pydantic import BaseModel, Field

load_dotenv(override=True)


class RefundEnum(str, Enum):
    """Enum for refund decision status."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RefundDecision(BaseModel):
    """A decision on whether to approve or reject a refund."""

    decision: RefundEnum = Field(
        ..., description="The refund decision - either APPROVED or REJECTED"
    )


def kill_switch(llm_review_decision: RefundDecision):
    """Kill the plan if the refund is rejected."""
    if llm_review_decision.decision == RefundEnum.REJECTED:
        raise Exception("Refund rejected. Fix your mistakes.")


def main(customer_email: str):
    with open("inbox.txt", "w") as f:
        f.write(customer_email)

    config = Config.from_default(default_log_level="INFO")

    tools = DefaultToolRegistry(config=config)

    tools.with_tool_description(
        "portia:mcp:mcp.stripe.com:create_refund",
        "The amount should be provided in cents without any decimal points, e.g 10.00 should be 1000. \
        The refund_reason should ONLY be one of the following:  duplicate, fraudulent, or requested_by_customer ",
    )

    portia = Portia(config=config, tools=tools, execution_hooks=CLIExecutionHooks())
    plan = (
        PlanBuilderV2("Run this plan to process a refund request.")
        .invoke_tool_step(
            step_name="read_refund_policy",
            args={"filename": "./refund_policy.txt"},
            tool="file_reader_tool",
        )
        .invoke_tool_step(
            step_name="read_refund_request",
            args={"filename": "inbox.txt"},
            tool="file_reader_tool",
        )
        .llm_step(
            step_name="llm_refund_review",
            task="Review the refund request against the refund policy. \
                Decide if the refund should be approved or rejected. \
                Return the decision in the format: 'APPROVED' or 'REJECTED'.",
            inputs=[
                StepOutput("read_refund_policy"),
                StepOutput("read_refund_request"),
            ],
            output_schema=RefundDecision,
        )
        .if_(
            condition=lambda llm_review_decision: llm_review_decision.decision
            == RefundEnum.REJECTED,
            args={"llm_review_decision": StepOutput("llm_refund_review")},
        )
        .function_step(
            step_name="send_rejection_email",
            function=kill_switch,
            args={"llm_review_decision": StepOutput("llm_refund_review")},
        )
        .endif()
        .llm_step(
            step_name="extract_email_address",
            task="Extract the customer's email address from the refund request email text.",
            inputs=[StepOutput("read_refund_request")],
        )
        .single_tool_agent_step(
            step_name="list_customers",
            task="List all customers including all fields returned from Stripe, filtered by the email address.",
            tool="portia:mcp:mcp.stripe.com:list_customers",
            inputs=[StepOutput("extract_email_address")],
        )
        .single_tool_agent_step(
            step_name="list_payment_intents",
            task="List all payment intents in Stripe for the target customer.",
            tool="portia:mcp:mcp.stripe.com:list_payment_intents",
            inputs=[StepOutput("list_customers")],
        )
        .user_verify(
            step_name="clarify_with_human",
            message=f"Are you happy to proceed with the refund for payment intent:\n \
                {StepOutput('list_payment_intents')}?\n Enter 'y' or 'yes' to proceed",
        )
        .single_tool_agent_step(
            step_name="create_refund",
            task="Create a refund for the target payment intent.",
            tool="portia:mcp:mcp.stripe.com:create_refund",
            inputs=[StepOutput("list_payment_intents")],
        )
        # .endif()
        .build()
    )

    print("Plan:")
    print(plan.model_dump_json(indent=2))
    portia.run_plan(plan)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="The email address of the customer. Should match the email address in Stripe.",
    )
    parser.add_argument(
        "--request",
        type=str,
        required=False,
        default="I bought one of your hoverboards 3 days ago. "
        "When I took it out of the box and turned it on, "
        "it did not work. Please can I get a refund?",
    )

    args = parser.parse_args()
    main(f"""---header---
        From: Marty McFly <email: {args.email}>
        To: support@hoverfly.com
        Subject: Refund request
        ---header---
        ---body---
        Hi,
        {args.request}

        Thanks,
        Marty McFly
        ---body---""")
