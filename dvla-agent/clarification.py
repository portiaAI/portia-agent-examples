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
        clarification_msg = f"{clarification.user_guidance or 'I need some additional information from you.'}"
        st.session_state.messages.append(
            {"role": "assistant", "content": clarification_msg}
        )

        # Force UI update to show message immediately
        st.rerun()
