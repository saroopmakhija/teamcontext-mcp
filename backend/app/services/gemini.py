import os
from google import genai

class GeminiService:
    def __init__(self, system_prompt: str):
        self.gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.system_prompt = system_prompt or "You are a helpful assistant that can answer questions and help with tasks."

    def generate_text(self, prompt: str) -> str:
        response = self.gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text


