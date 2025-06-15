import streamlit as st
from orchestrator.orchestrator import run_all_agents

st.title("🧠 MediMind: Clinical Case Review Assistant")

uploaded_file = st.file_uploader("Upload a case JSON file", type="json")

if uploaded_file:
    with open("data/temp_case.json", "wb") as f:
        f.write(uploaded_file.read())
    results = run_all_agents("data/temp_case.json")

    st.subheader("📋 Reflective Summary")
    st.markdown(results["reflective_summary"])
    st.subheader("🧠 Diagnostic Suggestions")
    st.markdown(results["diagnostic_suggestions"])
    st.subheader("💊 Medication Review")
    st.markdown(results["medication_review"])
