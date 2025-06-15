import json

class HistoryAgent:
    def __init__(self, case_path):
        self.case_path = case_path

    def run(self):
        with open(self.case_path, 'r') as file:
            case_data = json.load(file)

        age = case_data.get("age", "Unknown")
        sex = case_data.get("sex", "Unknown")
        history = ", ".join(case_data.get("medical_history", [])) or "None reported"
        symptoms = ", ".join(case_data.get("current_symptoms", [])) or "None reported"
        vitals = case_data.get("vital_signs", {})

        summary = (
            f"Patient is a {age}-year-old {sex}. "
            f"Medical history includes: {history}. "
            f"Current symptoms: {symptoms}. "
            f"Vital signs: "
            f"Temperature {vitals.get('temperature', 'N/A')}°F, "
            f"Blood Pressure {vitals.get('blood_pressure', 'N/A')}, "
            f"Heart Rate {vitals.get('heart_rate', 'N/A')} bpm."
        )

        return summary
