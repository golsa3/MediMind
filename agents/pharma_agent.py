class PharmaAgent:
    def __init__(self, case_data):
        self.case_data = case_data

    def run(self):
        meds = [m.lower() for m in self.case_data.get("medications", [])]
        alerts = []

        interaction_pairs = [
            ("lisinopril", "ibuprofen"),  # raises kidney risk
            ("metformin", "cimetidine"),  # affects metformin clearance
        ]

        for a, b in interaction_pairs:
            if a in meds and b in meds:
                alerts.append(f"⚠️ Potential interaction between {a} and {b}.")

        if not meds:
            alerts.append("⚠️ No medications listed — verify medication history.")

        if not alerts:
            alerts.append("✅ No medication concerns flagged.")

        return "\n".join(alerts)
