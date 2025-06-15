import streamlit as st
import tempfile
import base64
from orchestrator.orchestrator import run_all_agents

st.set_page_config(page_title="MediMind", page_icon="🧠", layout="centered")

st.title("🧠 MediMind: Multi-Agent Clinical Review")
st.markdown(
    """
Welcome to **MediMind**, your collaborative AI assistant for patient case review.  
Upload a structured `.json` patient summary and let our specialized agents flag diagnoses, risks, medication concerns, and clinical patterns.
"""
)

# File uploader
st.markdown("📁 **Upload a patient case (JSON)**")
uploaded_file = st.file_uploader("Drag and drop file here", type=["json"])

if uploaded_file is not None:
    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
            content = uploaded_file.read().decode("utf-8")
            tmp.write(content)
            case_path = tmp.name

        # Run agents
        results = run_all_agents(case_path)

        st.success("✅ Analysis complete. See results below.")

        # Display Results
        st.subheader("🩺 History Summary")
        st.write(results["history_summary"])

        st.subheader("🧠 Diagnostic Suggestions")
        st.write(results["diagnostic_suggestions"])

        st.subheader("💊 Medication Review")
        st.write(results["medication_review"])

        st.subheader("📋 Reflective Summary")
        st.markdown(results["reflective_summary"])

    except Exception as e:
        st.error("An error occurred while processing the file.")
        st.exception(e)
