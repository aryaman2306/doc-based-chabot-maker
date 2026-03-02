def build_prompt(
    instructions: str,
    context: str,
    question: str,
):
    """
    Builds strict RAG prompt.

    - instructions = base agent tone/personality
    - context = retrieved knowledge chunks
    - question = user input
    """

    return f"""
You are a knowledge-based assistant.

Follow these SYSTEM INSTRUCTIONS carefully:
{instructions}

STRICT RULES:
- Answer ONLY using the provided CONTEXT below.
- Do NOT use outside knowledge.
- If the answer is not present in the context, say:
  "I don't know based on the provided information."
- Do NOT invent information.
- Do NOT assume facts not present in the context.

CONTEXT:
{context}

USER QUESTION:
{question}

Provide a clear and direct answer.
""".strip()
