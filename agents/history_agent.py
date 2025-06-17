class HistoryAgent:
    def __init__(self, case_data):
        self.case_data = case_data

    def run(self):
        history = self.case_data.get("medical_history", [])
        summary = "📝 Medical History Summary:\n"

        if not history:
            summary += "- No medical history reported."
        else:
            for item in history:
                summary += f"- {item}\n"

        return summary.strip()
