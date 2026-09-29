"""Consultant Pulse navigation."""

import streamlit as st

st.set_page_config(page_title="Consultant Pulse", layout="wide")

navigation = st.navigation(
    {
        "Home": [
            st.Page("pages/dashboard.py", title="Dashboard", default=True),
        ],
        "Activities": [
            st.Page("pages/capture_feedback.py", title="Capture feedback"),
            st.Page("pages/report_individuals.py", title="Report on individuals"),
        ],
    }
)
navigation.run()
