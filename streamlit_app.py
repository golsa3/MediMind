import streamlit as st
from orchestrator.orchestrator import run_all_agents

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

    # Medications
    st.subheader("💊 Medications")
    medications = st.text_area("Current Medications (comma-separated)", value="Metformin, Lisinopril")

    submitted = st.form_submit_button("Run MediMind Review")

if submitted:
    st.success("✅ Case submitted. Running multi-agent review...")

    # Parse user input into dictionary
    try:
        case_data = {
            "age": age,
            "sex": sex,
            "weight": weight,
            "medical_history": [x.strip() for x in medical_history.split(",") if x.strip()],
            "current_symptoms": [x.strip() for x in current_symptoms.split(",") if x.strip()],
            "vital_signs": {
                k.strip(): v.strip()
                for k, v in (pair.split(":") for pair in vital_signs.split(",") if ":" in pair)
            },
            "medications": [x.strip() for x in medications.split(",") if x.strip()]
        }

        # Run MediMind review
        results = run_all_agents(case_data)

        st.header("🧠 MediMind Review Results")
        for key, value in results.items():
            st.subheader(f"🔍 {key.replace('_', ' ').title()}")
            st.markdown(value)

    except Exception as e:
        st.error(f"An error occurred while processing the case: {e}")
