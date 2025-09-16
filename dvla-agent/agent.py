from typing import Callable

import streamlit as st
from dotenv import load_dotenv
from models import (
    CarTaxPayment,
    DrivingLicenseApplication,
    DVLAQueryType,
    InstructionResponse,
    QueryType,
)
from portia import (
    Clarification,
    ClarificationHandler,
    Config,
    ExecutionHooks,
    InputClarification,
    LogLevel,
    StepOutput,
    logger,
)
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input
from portia.portia import Portia
from processing import (
    process_car_tax_payment,
    process_driving_license_application,
)

load_dotenv()


class UserMessageClarificationHandler(ClarificationHandler):
    """Handle user clarifications by sending a message to the user"""

    def handle_input_clarification(
        self,
        clarification: InputClarification,
        on_resolution: Callable[[Clarification, object], None],
        on_error: Callable[[Clarification, object], None],
    ) -> None:
        """Handle a user input clarification."""
        clarification_msg = f"{clarification.user_guidance or 'I need some additional information from you.'}"
        st.session_state.messages.append(
            {"role": "assistant", "content": clarification_msg}
        )

        # Force UI update to show message immediately
        st.rerun()


@st.cache_resource
def get_portia():
    config = Config.from_default(
        default_model="openai/gpt-4o",
        default_log_level=LogLevel.DEBUG,
    )

    return Portia(
        config=config,
        execution_hooks=ExecutionHooks(
            clarification_handler=UserMessageClarificationHandler()
        ),
    )


@st.cache_resource
def create_dvla_plan():
    return (
        PlanBuilderV2("DVLA Agent specialized in 3 key services")
        .input(
            name="previous_conversation",
            description="The previous conversation with the user",
        )
        .react_agent_step(
            step_name="classify_conversation",
            task="""Analyze the conversation and classify it into one of these 3 categories by setting query_type to the appropriate value:
            
            1. "question_for_instructions": User is asking for instructions on how they can do something related to DVLA (e.g., "How do I renew my license?", "How do I book a driving test?", "What documents do I need?", "How to register a vehicle?" etc.)
            Choose this for any question that can be answered with a search of the DVLA website / documentation.
            
            2. "process_driving_licence_application": User wants to apply for a new driving license (e.g., "I want to apply for a driving license", "Help me get a new license", "Process my license application")
            
            3. "pay_vehicle_tax": User wants to pay vehicle/car tax (e.g., "I need to pay my car tax", "Help me tax my vehicle", "Vehicle tax payment")
            
            4. "other": If the conversation doesn't clearly fit into any of the above 3 categories
            
            If it's "other", use the clarification tool to politely explain that you can only help with those 3 specific services and ask them to rephrase their request.
            
            IMPORTANT: 
            - Respond conversationally and naturally
            - When using the clarification tool, remember that your user_guidance text is sent directly to the user as-is""",
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=DVLAQueryType,
        )
        .if_(
            condition=lambda classification: classification.query_type
            == QueryType.INSTRUCTIONS,
            args={"classification": StepOutput("classify_conversation")},
        )
        .react_agent_step(
            step_name="answer_instruction_question",
            task="""Use the search tool to find relevant DVLA information and answer the user's question about DVLA instructions, procedures, or requirements. Search for official UK DVLA information related to their query. Provide a comprehensive, helpful answer with specific steps, requirements, and any important details.

            IMPORTANT:
            - Respond conversationally and naturally as if helping a friend
            - When using the clarification tool, remember that your user_guidance text is sent directly to the user as-is
            - Focus on being helpful and clear in your explanations""",
            tools=["search_tool"],
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=InstructionResponse,
        )
        .else_if_(
            condition=lambda classification: classification.query_type
            == QueryType.DRIVING_LICENSE,
            args={"classification": StepOutput("classify_conversation")},
        )
        .react_agent_step(
            step_name="collect_driving_license_information",
            task="""Collect all necessary information for a driving license application. Ask the user for their full name, date of birth, current address, phone number, email and if they're replacing an existing license (and its number). Make sure you get all required information before proceeding.

            IMPORTANT:
            - Respond conversationally and naturally, like you're helping someone through a form
            - When using the clarification tool, remember that your user_guidance text is sent directly to the user as-is
            - Be patient and encouraging as you collect the information""",
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=DrivingLicenseApplication,
        )
        .function_step(
            step_name="process_driving_license_application",
            function=process_driving_license_application,
            args={"application": StepOutput("collect_driving_license_information")},
        )
        .else_if_(
            condition=lambda classification: classification.query_type
            == QueryType.VEHICLE_TAX,
            args={"classification": StepOutput("classify_conversation")},
        )
        .react_agent_step(
            step_name="collect_car_tax_information",
            task="""Collect all necessary information for vehicle tax payment. Ask the user for their vehicle registration number, make and model, and the vehicle owner's name. Make sure you get all required information before proceeding.

            IMPORTANT:
            - Respond conversationally and naturally, like you're helping someone through a form
            - When using the clarification tool, remember that your user_guidance text is sent directly to the user as-is
            - Be patient and encouraging as you collect the information""",
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=CarTaxPayment,
        )
        .function_step(
            step_name="process_car_tax_payment",
            function=process_car_tax_payment,
            args={"payment": StepOutput("collect_car_tax_information")},
        )
        .else_()
        # We shouldn't enter this case
        .function_step(
            function=lambda: "I'm sorry, I can only help with DVLA instructions, driving license applications, or vehicle tax payments. Please let me know which of these I can help you with!",
        )
        .endif()
        .build()
    )


async def run_dvla_agent(conversation_history):
    """Run the DVLA agent with the conversation history"""
    portia = get_portia()
    plan = create_dvla_plan()

    conversation_text = "\n".join(
        [
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in conversation_history
        ]
    )

    try:
        plan_run = await portia.arun_plan(
            plan, plan_run_inputs={"previous_conversation": conversation_text}
        )

        if "$step_2_output" in plan_run.outputs.step_outputs:
            value = plan_run.outputs.step_outputs["$step_2_output"].get_value().answer
        elif "$step_5_output" in plan_run.outputs.step_outputs:
            value = plan_run.outputs.step_outputs["$step_5_output"].get_value()
        elif "$step_8_output" in plan_run.outputs.step_outputs:
            value = plan_run.outputs.step_outputs["$step_8_output"].get_value()
        else:
            value = "I'm sorry, I encountered an issue processing your request."

        return value + "\n\nPlease let me know if you need further assistance."

    except Exception as e:
        logger().error("Error processing request", e)
        return "I'm sorry, I encountered an issue processing your request. Please try again or rephrase your question."
