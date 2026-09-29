"""Manager dashboard. Landing page."""

from datetime import UTC, datetime, timedelta

import streamlit as st

RECENT_DAYS = 30

st.title("Consultant Pulse")
st.caption("Capture project feedback while it's fresh.")

observations = st.session_state.get("observations", [])
consultants = sorted({item["consultant"] for item in observations})
projects = sorted({item["project"] for item in observations})
cutoff = datetime.now(UTC) - timedelta(days=RECENT_DAYS)
without_feedback = [
    name
    for name in consultants
    if not any(item["consultant"] == name and item["submitted_at"] >= cutoff for item in observations)
]

cards = st.columns(4)
cards[0].metric("My consultants", len(consultants))
cards[1].metric("Active projects", len(projects))
cards[2].metric("Feedback this period", len(observations))
cards[3].metric("Without recent feedback", len(without_feedback))

st.divider()

actions = st.columns(2)
if actions[0].button("Give feedback", type="primary", use_container_width=True):
    st.switch_page("pages/capture_feedback.py")
if actions[1].button("Report on individuals", use_container_width=True):
    st.switch_page("pages/report_individuals.py")

st.subheader("Consultants")
st.caption("Counts are documented observations, not performance scores.")

if not consultants:
    st.info("No feedback has been captured in this session yet.")
else:
    rows = []
    for name in consultants:
        matched = [item for item in observations if item["consultant"] == name]
        last = max(item["submitted_at"] for item in matched)
        rows.append(
            {
                "Consultant": name,
                "Active projects": len({item["project"] for item in matched}),
                "Feedback count": len(matched),
                "Last feedback": last.strftime("%b %d, %Y"),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
