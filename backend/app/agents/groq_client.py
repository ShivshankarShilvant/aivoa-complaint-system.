import json
from groq import Groq

from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def call_groq(
    prompt: str,
    system: str = "",
    model: str = settings.GROQ_EXTRACTION_MODEL,
    json_mode: bool = False,
    temperature: float = 0.2,
) -> str:
    """Single call to a Groq-hosted model. Returns raw text content."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1024,
        **kwargs,
    )
    return resp.choices[0].message.content


def call_groq_json(prompt: str, system: str = "", model: str = settings.GROQ_EXTRACTION_MODEL) -> dict:
    """Call Groq expecting a JSON object back. Falls back to a best-effort
    parse + retry once if the model wraps the JSON in prose or fences."""
    raw = call_groq(prompt, system=system, model=model, json_mode=True)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Retry once with an explicit correction instruction
            retry_prompt = (
                f"Your previous response was not valid JSON:\n{raw}\n\n"
                "Return ONLY a valid JSON object, no prose, no markdown fences."
            )
            raw2 = call_groq(retry_prompt, system=system, model=model, json_mode=True)
            return json.loads(raw2)
