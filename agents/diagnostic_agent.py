import json

class DiagnosticAgent:
    def __init__(self, case_path):
        self.case_path = case_path

    def run(self):
        with open(self.case_path, 'r') as file:
            case_data = json.load(file)

        symptoms = case_data.get("current_symptoms", [])
        labs = case_data.get("labs", {})
        temp = case_data.get("vital_signs", {}).get("temperature", 98.6)

        differentials = []

        # Example logic
        if "abdominal pain" in [s.lower() for s in symptoms]:
            if labs.get("WBC", 0) > 11 or temp > 100.4:
                differentials.append("Cholecystitis (gallbladder inflammation)")
            else:
                differentials.append("Irritable Bowel Syndrome")

        if labs.get("Glucose", 0) > 180:
            differentials.append("Poorly controlled diabetes")

        if "fever" in [s.lower() for s in symptoms] and labs.get("WBC", 0) > 12:
            differentials.append("Possible infection")

        if not differentials:
            differentials.append("No clear diagnosis identified from current data.")

        return differentials
