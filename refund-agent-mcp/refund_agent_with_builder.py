"""Simple Example."""

import argparse
from enum import Enum

from dotenv import load_dotenv
from portia import Config, Input
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


class ProposedRefund(BaseModel):
    """A proposed refund."""

    payment_amount: int = Field(
        ..., description="The payment amount to be refunded in pounds."
    )
    description: str = Field(..., description="The description of the refund.")
    recipient_email: str = Field(
        ..., description="The email address of the recipient of the refund."
    )

    def __str__(self):
        return f"Payment amount: £{self.payment_amount}\nDescription: {self.description}\nRecipient email: {self.recipient_email}"


class RefundDecision(BaseModel):
    """A decision on whether to approve or reject a refund."""

    decision: RefundEnum = Field(
        ..., description="The refund decision - either APPROVED or REJECTED"
    )


def kill_switch(llm_review_decision: RefundDecision):
    """Kill the plan if the refund is rejected."""
    if llm_review_decision.decision == RefundEnum.REJECTED:
        raise Exception("Refund rejected. Fix your mistakes.")


def reject_payments_above_limit(proposed_refund: ProposedRefund, limit: int):
    """Reject any payments above the limit."""
    if proposed_refund.payment_amount > limit:
        raise Exception("Payment amount is too high. Refund rejected.")


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
        .input(
            name="payment_limit",
            description="The limit of the payment amount to be refunded.",
            default_value=1000,
        )
        .invoke_tool_step(
            step_name="read_refund_policy",
            args={"filename": "./refund_policy.txt"},
            tool="file_reader_tool",
        )
        # Uncomment if you would instead like to read from an email
        # .single_tool_agent_step(
        #     step_name="read_refund_request",
        #     task="Read the refund request from my inbox.",
        #     tool="portia:google:gmail:search_email",
        # )
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
        .llm_step(
            step_name="extract_proposed_refund",
            task="Extract the proposed refund from the payment intent (note that the amount is in pence, not pounds).",
            inputs=[
                StepOutput("list_payment_intents"),
                StepOutput("read_refund_request"),
            ],
            output_schema=ProposedRefund,
        )
        .user_verify(
            step_name="clarify_with_human",
            message=f"Are you happy to proceed with the following proposed refund:\n\n{StepOutput('extract_proposed_refund')}?\n\n Enter 'y' or 'yes' to proceed",
        )
        .function_step(
            step_name="reject_payments_above_limit",
            function=reject_payments_above_limit,
            args={
                "proposed_refund": StepOutput("extract_proposed_refund"),
                "limit": Input("payment_limit"),
            },
        )
        .single_tool_agent_step(
            step_name="create_refund",
            task="Create a refund for the target payment intent.",
            tool="portia:mcp:mcp.stripe.com:create_refund",
            inputs=[StepOutput("list_payment_intents")],
        )
        # Uncomment to send an email confirmation receipt
        # .single_tool_agent_step(
        #     step_name="confirm_refund",
        #     task="Send confirmation of the refund to the recipient.",
        #     tool="portia:google:gmail:send_email",
        #     inputs=[StepOutput("extract_proposed_refund")],
        # )
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
