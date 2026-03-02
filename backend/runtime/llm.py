# runtime/llm.py
import os
from openai import OpenAI


# ==============================
# Hugging Face Router (OpenAI API)
# ==============================

HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")
if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN (or HF_API_TOKEN) environment variable is not set"
    )

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

MODEL_ID = "moonshotai/Kimi-K2-Instruct-0905"


# ==============================
# LLM Call (Chat Completion)
# ==============================

def call_llm(prompt: str) -> str:
    """
    Uses Hugging Face Router via OpenAI-compatible API.
    This matches the working HF reference code exactly.
    """

    completion = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a knowledge-base assistant. "
                    "Answer ONLY using the provided context. "
                    "If the answer is not present, say you don't know."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    if not completion.choices:
        raise RuntimeError("Empty response from HF Router")

    return completion.choices[0].message.content.strip()

