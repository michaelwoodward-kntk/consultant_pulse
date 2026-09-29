"""TPM captures project feedback."""

from datetime import UTC, datetime

import streamlit as st

st.title("Capture feedback")
st.caption("Capture project feedback while it's fresh.")

with st.form("capture_feedback", clear_on_submit=True):
    project = st.text_input("Project", placeholder="Which project is this about?")
    consultant = st.text_input("Consultant", placeholder="Who is this feedback about?")
    feedback = st.text_area(
        "What happened?",
        placeholder="What did the consultant actually do?",
        help="Describe a specific action, behavior, decision, or accomplishment.",
    )
    submitted = st.form_submit_button("Submit feedback", type="primary")

if submitted:
    if not project.strip() or not consultant.strip() or not feedback.strip():
        st.error("Identify the project, the consultant, and the feedback before submitting.")
    else:
        st.session_state.setdefault("observations", []).append(
            {
                "project": project.strip(),
                "consultant": consultant.strip(),
                "feedback": feedback.strip(),
                "submitted_at": datetime.now(UTC),
            }
        )
        st.success("Feedback captured. Thank you for taking a moment to document the observation.")
