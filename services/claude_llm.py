# Claude LLM integration for chatbot
import os
import anthropic

class ClaudeLLM:
    def __init__(self, api_key=None, model="claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def ask(self, prompt):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text if response.content else "No response."
