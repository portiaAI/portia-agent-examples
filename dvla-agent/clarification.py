from typing import Callable

import streamlit as st
from portia import Clarification, ClarificationHandler, InputClarification


class ClarificationNeedException(Exception):
    """Exception raised when clarification is needed to break out of agent execution"""

    pass


class UserMessageClarificationHandler(ClarificationHandler):
    """Handler for user messages"""

    def handle_input_clarification(
        self,
        clarification: InputClarification,
        on_resolution: Callable[[Clarification, object], None],
        on_error: Callable[[Clarification, object], None],
    ) -> None:
        """Handle a user input clarification."""
        # Store the clarification in session state for handling in the UI
        st.session_state.pending_clarification = {
            "clarification": clarification,
            "on_resolution": on_resolution,
            "on_error": on_error,
            "message": clarification.user_guidance
            or "I need some additional information from you.",
        }

        # Add the clarification message to the conversation
        clarification_msg = f"🤔 {clarification.user_guidance or 'I need some additional information from you.'}"
        st.session_state.messages.append(
            {"role": "assistant", "content": clarification_msg}
        )

        # Set flag that we're waiting for clarification
        st.session_state.waiting_for_clarification = True

        # Force UI update to show clarification immediately
        try:
            st.rerun()
        except Exception:
            # If rerun fails (e.g., not in main thread), raise exception to break execution
            raise ClarificationNeedException("Clarification needed - forcing UI update")
