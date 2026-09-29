"""Manager views documented feedback for a consultant."""

import streamlit as st

st.title("Report on individuals")
st.caption("Documented observations for one consultant. Counts are observations, not a performance score.")

observations = st.session_state.get("observations", [])
consultants = sorted({item["consultant"] for item in observations})

if not consultants:
    st.info("No feedback has been captured in this session yet.")
else:
    selected = st.selectbox("Consultant", consultants)
    matched = [item for item in observations if item["consultant"] == selected]
    projects = sorted({item["project"] for item in matched})

    st.metric("Documented observations", len(matched))
    st.write(f"Projects: {len(projects)}")
    for project in projects:
        st.subheader(project)
        for item in matched:
            if item["project"] == project:
                st.write(item["feedback"])
