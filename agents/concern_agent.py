import json

class ConcernAgent:
    def __init__(self, case_path):
        self.case_path = case_path

    def run(self):
        with open(self.case_path, 'r') as file:
            case_data = json.load(file)

        concerns = []

        symptoms = case_data.get("current_symptoms", [])
        vitals = case_data.get("vital_signs", {})
        temp = vitals.get("temperature", None)

        # Check 1: Are symptoms missing?
        if not symptoms:
            concerns.append("⚠️ No current symptoms reported — is this intentional?")

        # Check 2: Are vitals incomplete?
        required_vitals = ["temperature", "blood_pressure", "heart_rate"]
        for key in required_vitals:
            if key not in vitals:
                concerns.append(f"⚠️ Missing vital sign: {key.replace('_', ' ').title()}")

        # Check 3: Conflicting logic
        if "fever" in [s.lower() for s in symptoms] and temp is not None and temp < 99:
            concerns.append("⚠️ 'Fever' is listed as a symptom but temperature is below 99°F.")

        # Check 4: Is lab data too limited?
        if len(case_data.get("labs", {})) < 3:
            concerns.append("⚠️ Limited lab data — consider ordering more tests.")

        if not concerns:
            concerns.append("✅ No major concerns flagged.")

        return concerns
