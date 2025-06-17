
import streamlit as st
import json
import tempfile
from orchestrator.orchestrator import run_all_agents
from vertexai.generative_models import GenerativeModel
import vertexai

st.set_page_config(page_title="MediMind: Multi-Agent Clinical Review", page_icon="🧠")

st.title("🧠 MediMind: Multi-Agent Clinical Review")
st.markdown(
    """
Welcome to **MediMind**, your collaborative AI assistant for patient case review.
Fill out the form below to generate a case. MediMind's specialized agents will flag diagnoses, risks, medication concerns, and clinical patterns.
"""
)

with st.form("patient_case_form"):
    st.header("📋 Patient Case Information")

    # Demographics
    st.subheader("🧍 Demographics")
    age = st.number_input("Age", min_value=0, max_value=120, value=45)
    sex = st.selectbox("Sex", ["M", "F", "Other"])
    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0)

    # Medical Info
    st.subheader("🩺 Medical Information")
    medical_history = st.text_area("Medical History (comma-separated)", value="Hypertension, Diabetes")
    current_symptoms = st.text_area("Current Symptoms (comma-separated)", value="Fever, Fatigue")
    vital_signs = st.text_area("Vital Signs (key:value, comma-separated)", value="Temp:101.2, BP:140/90, HR:95")
    labs = st.text_area("Lab Results (key:value, comma-separated)", value="")

    # Medications
    st.subheader("💊 Medications")
    medications = st.text_area("Current Medications (comma-separated)", value="Metformin, Lisinopril")

    # Submit
    submitted = st.form_submit_button("Run MediMind Review")

if submitted:
    msg_placeholder = st.empty()
    msg_placeholder.success("✅ Case submitted. Running multi-agent review...")

    patient_case = {
        "age": age,
        "sex": sex,
        "weight": weight,
        "medical_history": [x.strip() for x in medical_history.split(",") if x.strip()],
        "current_symptoms": [x.strip() for x in current_symptoms.split(",") if x.strip()],
        "vital_signs": {k.strip(): v.strip() for k, v in (pair.split(":") for pair in vital_signs.split(",") if ":" in pair)},
        "medications": [x.strip() for x in medications.split(",") if x.strip()],
        "labs": {k.strip(): v.strip() for k, v in (pair.split(":") for pair in labs.split(",") if ":" in pair)},
    }

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(patient_case, tmp)
        tmp.seek(0)
        results = run_all_agents(tmp.name)

    msg_placeholder.success("✅ Review complete. See results below:")

    st.header("🧠 MediMind Review Results")
    for key, value in results.items():
        formatted_key = key.replace("_", " ").title()
        with st.expander(f"🔍 {formatted_key}"):
            st.markdown(f"<div style='color:#333;background-color:#f0f2f6;padding:10px;border-radius:5px;'>{value}</div>", unsafe_allow_html=True)

    with st.expander("➕ Add Missing Info (Optional)"):
        user_additions = st.text_area("Add any missing info the AI asked for (e.g. family history, recent labs, exam findings):")

        if user_additions.strip():
            st.success("✅ Updating case with new information and re-running analysis...")
            vertexai.init(project="vital-valor-462719-n9", location="us-central1")
            model = GenerativeModel("gemini-2.0-flash")
            summary_text = json.dumps(patient_case, indent=2)

            prompt = (
                "You're an advanced clinical assistant. The following patient case and user additions are to be analyzed:

"
                f"Patient Case:
{summary_text}

"
                f"User Additions:
{user_additions.strip()}

"
                "Please generate an updated reflection considering the new details. Organize insights by category."
            )

            response = model.generate_content(prompt)
            with st.expander("🆕 Updated Reflective Summary"):
                st.markdown(response.text)
