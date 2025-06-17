class DiagnosticAgent:
    def __init__(self, case_data):
        self.case_data = case_data

    def run(self):
        symptoms = [s.lower() for s in self.case_data.get("current_symptoms", [])]
        history = [h.lower() for h in self.case_data.get("medical_history", [])]

        possible_conditions = []

        if "fever" in symptoms and "cough" in symptoms:
            possible_conditions.append("🦠 Possible respiratory infection (e.g., flu, COVID-19).")

        if "fatigue" in symptoms and "anemia" in history:
            possible_conditions.append("🩸 Consider evaluating for anemia recurrence.")

        if not possible_conditions:
            possible_conditions.append("✅ No diagnostic flags raised based on available data.")

        return "\n".join(possible_conditions)
