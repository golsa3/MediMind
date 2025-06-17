from vertexai.generative_models import GenerativeModel
import vertexai

class ReflectiveSummaryAgent:
    def __init__(self, summary):
        self.summary = summary

    def run(self):
        vertexai.init(project="vital-valor-462719-n9", location="us-central1")

        model = GenerativeModel("gemini-2.0-flash")

        prompt = (
            "You are a highly skilled multidisciplinary physician and clinical reasoning expert. You are reviewing the following patient case summary:\n\n"
            f"{self.summary}\n\n"
            "Based on this information, identify any overlooked patterns, inconsistencies, risk factors, or urgent red flags. Organize your response by clinical category (e.g., medical history, medications, vitals, symptoms, differential diagnosis, missing information). Provide practical and specific insights as if preparing this for a clinical handoff or triage escalation. Avoid generic statements and focus on meaningful observations that could guide diagnosis or further workup."

        )

        response = model.generate_content(prompt)
        return response.text.strip()
