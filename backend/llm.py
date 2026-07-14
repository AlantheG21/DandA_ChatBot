import anthropic
import os
from dotenv import load_dotenv

from prompts import build_system_prompt

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def ask_llm(user_prompt: str, retrieved_chunks: list[dict]) -> str:

    system_prompt = build_system_prompt(retrieved_chunks)

    message = client.messages.create(
        model = "claude-haiku-4-5-20251001",
        max_tokens = 512,
        system = system_prompt,
        messages = [
            {
                "role": "user",
                "content": user_prompt
            }
        ],
    )

    return message.content[0].text if message.content else "No response generated."