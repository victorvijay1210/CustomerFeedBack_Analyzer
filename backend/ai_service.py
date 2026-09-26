import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

ALLOWED_SENTIMENTS = {"Positive", "Negative", "Neutral"}


def _extract_json(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("No analysis returned")

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("No analysis returned")
    return json.loads(match.group(0))


def _validate_result(payload: dict[str, Any]) -> dict[str, str]:
    sentiment = str(payload.get("sentiment") or "").strip()
    explanation = str(payload.get("explanation") or "").strip()

    if sentiment not in ALLOWED_SENTIMENTS:
        raise ValueError("Unable to analyze feedback. Please try again.")
    if not explanation:
        raise ValueError("Unable to analyze feedback. Please try again.")

    return {"sentiment": sentiment, "explanation": explanation}


def analyze_sentiment(review: str) -> dict[str, str]:
    cleaned_review = review.strip()
    if not cleaned_review:
        raise ValueError("Please enter customer feedback.")

    if client is None:
        raise RuntimeError("Unable to analyze feedback. Please try again.")

    prompt = f"""
Analyze the following customer feedback.

Customer feedback:
{cleaned_review}

Classify the sentiment into exactly one of: Positive, Negative, Neutral.
Also provide a short explanation.

Return valid JSON only with this structure:
{{
  "sentiment": "Positive|Negative|Neutral",
  "explanation": "short explanation"
}}
""".strip()

    try:
        gemini_response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        raw_text = getattr(gemini_response, "text", "") or ""
        data = _extract_json(raw_text)
        return _validate_result(data)
    except Exception as exc:
        raise RuntimeError("Unable to analyze feedback. Please try again.") from exc
