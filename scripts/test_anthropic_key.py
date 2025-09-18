
import os
from dotenv import load_dotenv
import anthropic
from pathlib import Path

# Explicitly load .env from ask_data/.env
env_path = Path(__file__).parent.parent / "ask_data" / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("ANTHROPIC_API_KEY")
print("Loaded API key:", repr(api_key))

client = anthropic.Anthropic(api_key=api_key)
try:
    response = client.messages.create(
        model="claude-3-haiku",  # Changed to 'claude-3-haiku' for broader access
        max_tokens=10,
        temperature=0.0,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print("API call succeeded! Response:", response.content[0].text)
except Exception as e:
    print("API call failed:", e)