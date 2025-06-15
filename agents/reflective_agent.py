from vertexai.generative_models import GenerativeModel
import vertexai

class ReflectiveSummaryAgent:
    def __init__(self, summary):
        self.summary = summary

    def run(self):
        vertexai.init(project="vital-valor-462719-n9", location="us-central1")

        model = GenerativeModel("gemini-2.0-flash")

        prompt = (
            "You are a clinical assistant reviewing this patient case summary:\n\n"
            f"{self.summary}\n\n"
            "Please reflect on the case and flag any overlooked patterns, risks, or concerns."
        )

        response = model.generate_content(prompt)
        return response.text.strip()
