import asyncio

import streamlit as st
from agent import run_dvla_agent
from clarification import ClarificationNeedException
from dotenv import load_dotenv

# Load environment variables at app startup
load_dotenv()


def send_clarification_message(message: str) -> str:
    """Function to send a clarification message to the user"""
    formatted_message = f"🤖 {message}"
    st.session_state.messages.append(
        {"role": "assistant", "content": formatted_message}
    )
    return formatted_message


def send_final_answer(answer: str) -> str:
    """Send the final answer to the user"""
    formatted_answer = f"📋 {answer}"
    st.session_state.messages.append({"role": "assistant", "content": formatted_answer})
    return formatted_answer


def send_message(message, conversation_history):
    """Send a message and get response from the DVLA agent"""
    # Check if we're waiting for a clarification response
    if st.session_state.get("waiting_for_clarification", False):
        # Handle clarification response
        pending = st.session_state.get("pending_clarification")
        if pending:
            # Add user response to history
            conversation_history.append({"role": "user", "content": message})

            try:
                # Resolve the clarification with user's response
                pending["on_resolution"](pending["clarification"], message)

                # Clear clarification state and set continuing flag
                st.session_state.waiting_for_clarification = False
                if "pending_clarification" in st.session_state:
                    del st.session_state.pending_clarification
                st.session_state.continuing_after_clarification = True

                # After clarification is resolved, re-run the agent with the full conversation
                # This allows the agent to continue processing with the clarification response
                try:
                    # Re-run the agent with the full conversation including clarification
                    raw_response = asyncio.run(run_dvla_agent(conversation_history))

                    # Clear the continuing flag since we're done processing
                    if "continuing_after_clarification" in st.session_state:
                        del st.session_state.continuing_after_clarification

                    # Process the final response
                    if isinstance(raw_response, dict) and "answer" in raw_response:
                        return send_final_answer(raw_response["answer"])
                    elif isinstance(raw_response, str) and raw_response in [
                        "DRIVING_LICENSE_PROCESSED",
                        "CAR_TAX_PROCESSED",
                    ]:
                        # These processing functions have already added their messages to the chat
                        # Just return a simple success message (won't be displayed)
                        return "PROCESSED_SUCCESSFULLY"
                    else:
                        response_str = str(raw_response)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response_str}
                        )
                        return response_str

                except ClarificationNeedException:
                    # If another clarification is needed, clear continuing flag
                    if "continuing_after_clarification" in st.session_state:
                        del st.session_state.continuing_after_clarification
                    # Handle it in the next iteration
                    return "CLARIFICATION_PENDING"
                except Exception as continue_error:
                    # Clear continuing flag on error
                    if "continuing_after_clarification" in st.session_state:
                        del st.session_state.continuing_after_clarification
                    error_msg = f"❌ Error continuing after clarification: {str(continue_error)}"
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
                    return error_msg

            except Exception as e:
                # Handle error in clarification resolution
                pending["on_error"](pending["clarification"], str(e))

                # Clear clarification state and any continuing flag
                st.session_state.waiting_for_clarification = False
                if "pending_clarification" in st.session_state:
                    del st.session_state.pending_clarification
                if "continuing_after_clarification" in st.session_state:
                    del st.session_state.continuing_after_clarification

                return f"❌ Sorry, there was an error processing your clarification: {str(e)}"

    # Normal message processing
    # Add user message to history
    conversation_history.append({"role": "user", "content": message})

    # Run the agent asynchronously - handle clarification interruptions
    try:
        raw_response = asyncio.run(run_dvla_agent(conversation_history))
    except ClarificationNeedException:
        # Clarification is needed - the message has already been added to session state
        # The clarification handler will have tried st.rerun() already, but if that failed,
        # we return a signal to force a rerun in the UI layer
        return "CLARIFICATION_PENDING"

    # Format and send the response based on its type
    if isinstance(raw_response, dict) and "answer" in raw_response:
        # This is an InstructionResponse - use send_final_answer
        formatted_response = send_final_answer(raw_response["answer"])
    elif isinstance(raw_response, str) and raw_response in [
        "DRIVING_LICENSE_PROCESSED",
        "CAR_TAX_PROCESSED",
    ]:
        # These processing functions have already added their messages to the chat
        # Return a simple success indicator (won't be displayed in UI)
        formatted_response = "PROCESSED_SUCCESSFULLY"
    else:
        # Default handling for other response types
        formatted_response = str(raw_response)
        conversation_history.append(
            {"role": "assistant", "content": formatted_response}
        )

    return formatted_response


def main():
    st.title("🚗 DVLA Specialized Assistant")
    st.write("I can help you with these 3 specific DVLA services:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            "📋 **Instructions & How-To**\n\nAsk me how to do something DVLA-related"
        )

    with col2:
        st.success(
            "🆔 **Driving License Application**\n\nApply for a new driving license"
        )

    with col3:
        st.warning("💷 **Vehicle Tax Payment**\n\nPay tax for your vehicle")

    # Initialize session state for conversation history and clarifications
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "waiting_for_clarification" not in st.session_state:
        st.session_state.waiting_for_clarification = False
    if "pending_clarification" not in st.session_state:
        st.session_state.pending_clarification = None
    if "continuing_after_clarification" not in st.session_state:
        st.session_state.continuing_after_clarification = False

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input - adjust prompt based on clarification state
    if st.session_state.get("waiting_for_clarification", False):
        chat_placeholder = "Please provide the requested information..."
    elif st.session_state.get("continuing_after_clarification", False):
        chat_placeholder = "Processing your response..."
    else:
        chat_placeholder = (
            "How can I help you? (Instructions, License Application, or Vehicle Tax)"
        )

    if prompt := st.chat_input(chat_placeholder):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Show appropriate spinner based on context
        with st.chat_message("assistant"):
            # Determine spinner message based on current state
            if st.session_state.get("waiting_for_clarification", False):
                spinner_text = "Processing..."
            else:
                spinner_text = "Thinking..."

            with st.spinner(spinner_text):
                # Get response from DVLA agent
                response = send_message(prompt, st.session_state.messages)

                # Handle special cases
                if response == "CLARIFICATION_PENDING":
                    st.rerun()
                elif response == "PROCESSED_SUCCESSFULLY":
                    # Processing functions have already added their messages - don't display this
                    pass
                else:
                    st.markdown(response)

    # Sidebar with conversation controls
    with st.sidebar:
        # Show status based on current state
        if st.session_state.get("waiting_for_clarification", False):
            st.warning(
                "🤔 **Waiting for clarification**\n\nPlease respond to the agent's question in the chat."
            )
            st.divider()
        elif st.session_state.get("continuing_after_clarification", False):
            st.info(
                "⏳ **Processing your response**\n\nThank you for the clarification. Processing your request..."
            )
            st.divider()

        st.header("💡 Example Prompts")

        st.subheader("📋 Instructions")
        st.write("• How do I renew my driving license?")
        st.write("• What documents do I need to register a vehicle?")
        st.write("• How to change my address on my license?")

        st.subheader("🆔 License Application")
        st.write("• I want to apply for a driving license")
        st.write("• Help me get a provisional license")
        st.write("• Process my license application")

        st.subheader("💷 Vehicle Tax")
        st.write("• I need to pay my car tax")
        st.write("• Help me tax my vehicle")
        st.write("• Vehicle tax payment")

        st.divider()

        st.header("Chat Controls")
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

        st.subheader("Conversation History")
        if st.session_state.messages:
            for i, msg in enumerate(st.session_state.messages):
                role = "🧑‍💻" if msg["role"] == "user" else "🤖"
                preview = (
                    msg["content"][:50] + "..."
                    if len(msg["content"]) > 50
                    else msg["content"]
                )
                st.text(f"{role} {preview}")
        else:
            st.text("No messages yet")


if __name__ == "__main__":
    main()
