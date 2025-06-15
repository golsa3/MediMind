import streamlit as st
import json
from orchestrator.orchestrator import run_all_agents
from io import StringIO

st.set_page_config(page_title="MediMind", page_icon="🧠", layout="centered")
st.title("🧠 MediMind: Multi-Agent Clinical Review")

st.markdown("""
Welcome to **MediMind**, your collaborative AI assistant for patient case review.  
Upload a structured `.json` patient summary and let our specialized agents flag diagnoses, risks, medication concerns, and clinical patterns.
""")

uploaded_file = st.file_uploader("📁 Upload a patient case (JSON)", type=["json"])

if uploaded_file:
    case_data = json.load(uploaded_file)

    with st.expander("📄 Patient Case Summary"):
        st.json(case_data)

    if st.button("🚀 Run MediMind Agents"):
        with st.spinner("Running agents and analyzing case..."):
            results = run_all_agents(uploaded_file)

        st.success("Analysis complete! Review the results below:")

        with st.expander("💊 Medication Review"):
            st.markdown(results.get("pharma_risks", "No data."))

        with st.expander("⚠️ Risk Flags & Concerns"):
            st.markdown(results.get("concern_flags", "No concerns flagged."))

        with st.expander("🧠 Diagnostic Suggestions"):
            for diagnosis in results.get("diagnoses", []):
                st.markdown(f"- {diagnosis}")

        with st.expander("📝 Reflective Summary"):
            st.markdown(results.get("reflective_summary", "No summary available."))

        # Generate report
        report_md = f"""# MediMind Case Review Report

## 💊 Medication Review
{results.get("pharma_risks", "No data.")}

## ⚠️ Risk Flags & Concerns
{results.get("concern_flags", "None.")}

## 🧠 Diagnostic Suggestions
{chr(10).join(f"- {d}" for d in results.get("diagnoses", []))}

## 📝 Reflective Summary
{results.get("reflective_summary", "N/A")}
"""
        st.download_button(
            label="⬇️ Download Full Report",
            data=report_md,
            file_name="medimind_case_report.md",
            mime="text/markdown"
        )
