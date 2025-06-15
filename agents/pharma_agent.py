import json

class PharmaAgent:
    def __init__(self, case_path):
        self.case_path = case_path

    def run(self):
        with open(self.case_path, 'r') as file:
            case_data = json.load(file)

        meds = [m.lower() for m in case_data.get("medications", [])]

        interaction_db = {
            ("metformin", "lisinopril"): "⚠️ Risk of lactic acidosis when combined.",
            ("acetaminophen", "alcohol"): "⚠️ Liver toxicity risk with concurrent use.",
            ("ibuprofen", "lisinopril"): "⚠️ May reduce kidney function."
        }

        flagged = []
        for (med1, med2), warning in interaction_db.items():
            if med1 in meds and med2 in meds:
                flagged.append(warning)

        if not flagged:
            flagged.append("✅ No major drug interactions detected.")

        return flagged
