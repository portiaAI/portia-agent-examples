from clarification import UserMessageClarificationHandler
from dotenv import load_dotenv
from models import (
    CarTaxPayment,
    DrivingLicenseApplication,
    DVLAQueryType,
    InstructionResponse,
)
from portia import Config, ExecutionHooks, StepOutput, logger
from portia.builder.plan_builder_v2 import PlanBuilderV2
from portia.builder.reference import Input
from portia.portia import Portia
from processing import (
    process_car_tax_payment,
    process_driving_license_application,
)

load_dotenv()


def get_portia():
    config = Config.from_default()

    return Portia(
        config=config,
        execution_hooks=ExecutionHooks(
            clarification_handler=UserMessageClarificationHandler()
        ),
    )


def create_dvla_plan():
    plan = (
        PlanBuilderV2("DVLA Agent specialized in 3 key services")
        .input(
            name="previous_conversation",
            description="The previous conversation with the user",
        )
        # Step 1: Classify the conversation
        .react_agent_step(
            step_name="classify_conversation",
            task="""Analyze the conversation and classify it into one of these 3 categories by setting query_type to the appropriate value:
            
            1. "question_for_instructions": User is asking for instructions on how to do something related to DVLA (e.g., "How do I renew my license?", "What documents do I need?", "How to register a vehicle?")
            
            2. "process_driving_licence_application": User wants to apply for a new driving license (e.g., "I want to apply for a driving license", "Help me get a new license", "Process my license application")
            
            3. "pay_vehicle_tax": User wants to pay vehicle/car tax (e.g., "I need to pay my car tax", "Help me tax my vehicle", "Vehicle tax payment")
            
            4. "other": If the conversation doesn't clearly fit into any of the above 3 categories
            
            If it's "other", use the clarification tool to politely explain that you can only help with:
            - Answering questions about DVLA instructions and procedures
            - Processing new driving license applications  
            - Processing vehicle tax payments
            
            Ask them to rephrase their request to fit one of these categories.""",
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=DVLAQueryType,
        )
        # Branch 1: Instructions
        .if_(
            condition=lambda classification: classification.query_type
            == "question_for_instructions",
            args={"classification": StepOutput("classify_conversation")},
        )
        .react_agent_step(
            task="Use the search tool to find relevant DVLA information and answer the user's question about DVLA instructions, procedures, or requirements. Search for official UK DVLA information related to their query. Provide a comprehensive, helpful answer with specific steps, requirements, and any important details.",
            tools=["search_tool"],
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=InstructionResponse,
        )
        # Branch 2: Driving License Application
        .else_if_(
            condition=lambda classification: classification.query_type
            == "process_driving_licence_application",
            args={"classification": StepOutput("classify_conversation")},
        )
        .react_agent_step(
            step_name="collect_driving_license_information",
            task="Collect all necessary information for a driving license application. Ask the user for their full name, date of birth, current address, phone number, email, what type of license they want, and if they're replacing an existing license (and its number). Make sure you get all required information before proceeding.",
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=DrivingLicenseApplication,
        )
        .function_step(
            function=process_driving_license_application,
            args={"application": StepOutput("collect_driving_license_information")},
        )
        # Branch 3: Car Tax Payment
        .else_if_(
            condition=lambda classification: classification.query_type
            == "pay_vehicle_tax",
            args={"classification": StepOutput("classify_conversation")},
        )
        .react_agent_step(
            step_name="collect_car_tax_information",
            task="Collect all necessary information for vehicle tax payment. Ask the user for their vehicle registration number, make and model, vehicle type, engine size (if applicable), fuel type, how long they want to tax it for (6 or 12 months), and the vehicle owner's name. Make sure you get all required information before proceeding.",
            inputs=[Input("previous_conversation")],
            allow_agent_clarifications=True,
            output_schema=CarTaxPayment,
        )
        .function_step(
            function=process_car_tax_payment,
            args={"payment": StepOutput("collect_car_tax_information")},
        )
        # Default case: Should not happen due to clarification in first step
        .else_()
        .function_step(
            function=lambda: "I'm sorry, I can only help with DVLA instructions, driving license applications, or vehicle tax payments. Please let me know which of these I can help you with!",
        )
        .endif()
        .build()
    )
    return plan


async def run_dvla_agent(conversation_history):
    """Run the DVLA agent with the conversation history"""
    portia = get_portia()
    plan = create_dvla_plan()

    # Format conversation history as a string
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

        # Extract the response from the plan run result - hide internal details
        if hasattr(plan_run, "result") and plan_run.result:
            return plan_run.result
        elif hasattr(plan_run, "outputs") and hasattr(plan_run.outputs, "final_output"):
            # Try to get final output value
            if hasattr(plan_run.outputs.final_output, "value"):
                return plan_run.outputs.final_output.value
            else:
                return plan_run.outputs.final_output
        else:
            # Return a user-friendly message instead of dumping internal data
            return "I've processed your request. If you need further assistance, please let me know!"

    except Exception:
        logger().error("Error processing request", exc_info=True)
        return "I'm sorry, I encountered an issue processing your request. Please try again or rephrase your question."
