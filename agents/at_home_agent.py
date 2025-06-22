from vertexai.generative_models import GenerativeModel
import vertexai

vertexai.init(project="vital-valor-462719-n9", location="us-central1")

def generate_precautions(patient_case_summary: str, reflection_summary: str) -> str:
    """
    Uses Gemini to generate at-home care advice based on the patient summary and AI's reflection.
    """
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are a clinical AI assistant. Based on the following patient case and AI reflection, generate a list of tailored at-home care precautions.
Focus on non-emergency support for symptom relief, safe practices, and lifestyle tips.

Patient Case:
{patient_case_summary}

AI Reflection:
{reflection_summary}

Return just a clean, concise list of at-home tips.
"""

    response = model.generate_content(prompt)
    return response.text.strip()
