import asyncio

import streamlit as st
from agent import run_dvla_agent
from dotenv import load_dotenv

# Load environment variables at app startup
load_dotenv()


def send_message(message, conversation_history):
    """Send a message and get response from the DVLA agent"""
    conversation_history.append({"role": "user", "content": message})

    response = asyncio.run(run_dvla_agent(conversation_history))

    st.session_state.messages.append({"role": "assistant", "content": response})

    return response


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

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    chat_placeholder = (
        "How can I help you? (Instructions, License Application, or Vehicle Tax)"
    )

    if prompt := st.chat_input(chat_placeholder):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt, st.session_state.messages)

                if response == "CLARIFICATION_PENDING":
                    st.rerun()
                elif response == "PROCESSED_SUCCESSFULLY":
                    pass
                else:
                    st.markdown(response)

    with st.sidebar:
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
