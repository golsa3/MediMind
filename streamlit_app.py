
import streamlit as st
import json
from orchestrator.orchestrator import run_all_agents
import tempfile

st.set_page_config(page_title="MediMind: Multi-Agent Clinical Review", page_icon="🧠")

st.title("🧠 MediMind: Multi-Agent Clinical Review")
st.markdown(
    '''
Welcome to **MediMind**, your collaborative AI assistant for patient case review.

Fill out the form below to generate a case. MediMind's specialized agents will flag diagnoses, risks, medication concerns, and clinical patterns.
'''
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

    # Vitals
    st.subheader("🩸 Vital Signs")
    temp = st.number_input("Temperature (°F)", min_value=85.0, max_value=110.0, value=101.2)
    bp = st.text_input("Blood Pressure (e.g., 120/80)", value="140/90")
    hr = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=95)

    # Medications
    st.subheader("💊 Medications")
    medications = st.text_area("Current Medications (comma-separated)", value="Metformin, Lisinopril")

    # Optional fields
    st.subheader("🧬 Additional Information (Optional)")
    family_history = st.text_area("Family History", value="")
    physical_exam = st.text_area("Physical Exam Findings", value="")

    submitted = st.form_submit_button("Run MediMind Review")

if submitted:
    status_text = st.empty()
    status_text.success("✅ Case submitted. Running multi-agent review...")

    patient_case = {
        "age": age,
        "sex": sex,
        "weight": weight,
        "medical_history": [x.strip() for x in medical_history.split(",") if x.strip()],
        "current_symptoms": [x.strip() for x in current_symptoms.split(",") if x.strip()],
        "vital_signs": {
            "temperature": temp,
            "blood_pressure": bp,
            "heart_rate": hr
        },
        "medications": [x.strip() for x in medications.split(",") if x.strip()],
        "family_history": family_history.strip(),
        "physical_exam": physical_exam.strip()
    }

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        json.dump(patient_case, tmp)
        tmp.seek(0)
        results = run_all_agents(tmp.name)

    status_text.success("✅ Review complete. See results below:")

    st.header("🧠 MediMind Review Results")
    for key, value in results.items():
        with st.expander(f"🔍 {key.replace('_', ' ').title()}", expanded=True):
            st.markdown(f"<div style='font-size:15px; line-height:1.6'>{value}</div>", unsafe_allow_html=True)
