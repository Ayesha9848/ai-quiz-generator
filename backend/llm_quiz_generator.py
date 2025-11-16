"""
Gemini integration (google-generativeai) + deterministic fallback.

Requires:
pip install google-generativeai
Put GEMINI_API_KEY into backend/.env (optional). If not present, code uses fallback.
"""

import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5")
GEMINI_AVAILABLE = bool(GEMINI_KEY)

try:
    import google.generativeai as genai
    if GEMINI_AVAILABLE:
        genai.configure(api_key=GEMINI_KEY)
except Exception:
    genai = None

from pydantic import ValidationError
from .models import QuizOutput

PROMPT_INSTRUCTIONS = """
You are an assistant that MUST produce a strict JSON object matching this schema (no extra explanation).

Schema keys:
- title (string)
- summary (string, 2-4 sentences, grounded in ARTICLE_TEXT)
- key_entities { people: [], organizations: [], locations: [] }
- sections: list of section headings
- quiz: list of 5-10 question objects where each question has:
    - question (string)
    - options (list of 4 strings)
    - answer (one of the options)
    - explanation (short grounded explanation)
    - difficulty (one of: easy, medium, hard)
- related_topics: list of 3-6 related wikipedia topics (strings)

Important constraints:
- Output ONLY valid JSON. Do not include preface, commentary, or markdown.
- When facts are not present in the article, say "not mentioned in article" for the field.
"""

def _extract_json_from_text(text: str) -> str:
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found in model output")
    stack = []
    for i in range(start, len(text)):
        ch = text[i]
        if ch == '{':
            stack.append('{')
        elif ch == '}':
            if not stack:
                continue
            stack.pop()
            if not stack:
                return text[start:i+1]
    raise ValueError("Failed to find matching closing brace in model output")

def _call_gemini_chat(prompt: str, model: str = GEMINI_MODEL, temperature: float = 0.0) -> str:
    if genai is None:
        raise RuntimeError("google.generativeai client is not installed or not importable")
    resp = genai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROMPT_INSTRUCTIONS},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_output_tokens=1600,
    )
    # handle different response shapes
    if hasattr(resp, "candidates") and resp.candidates:
        return resp.candidates[0].content
    if isinstance(resp, dict) and resp.get("candidates"):
        return resp["candidates"][0]["content"]
    # fallback
    return str(resp)

def generate_quiz_from_text(article_text: str, title: str, sections: list) -> dict:
    if GEMINI_AVAILABLE and genai is not None:
        user_prompt = f"ARTICLE_TITLE: {title}\n\nARTICLE_TEXT:\n" + article_text[:50000]
        raw = _call_gemini_chat(user_prompt)
        cleaned = raw.strip()
        cleaned = re.sub(r"^```\\w*", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned).strip()
        try:
            json_text = _extract_json_from_text(cleaned)
        except ValueError as e:
            raise RuntimeError(f"Failed to extract JSON from model output: {e}\nRaw: {cleaned[:2000]}")
        try:
            obj = json.loads(json_text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse JSON: {e}\nCandidate: {json_text[:2000]}")
        try:
            validated = QuizOutput.parse_obj(obj)
            return json.loads(validated.json())
        except ValidationError as ve:
            raise RuntimeError(f"Validation failed: {ve}\nKeys: {list(obj.keys())}")

    # Fallback deterministic generator
    sentences = [s.strip() for s in article_text.split('.') if len(s.strip()) > 30]
    quiz = []
    for i in range(min(5, len(sentences))):
        sent = sentences[i]
        words = sent.split()
        if len(words) < 6:
            continue
        answer = words[-1].strip(" .")
        question_text = sent.replace(answer, "_____")
        options = [answer, "Option A", "Option B", "Option C"]
        quiz.append({
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": f"From the article: {sent[:120]}...",
            "difficulty": "easy" if i < 2 else "medium"
        })
    output = {
        "title": title,
        "summary": "\n".join(sentences[:2]) if sentences else title,
        "key_entities": {"people": [], "organizations": [], "locations": []},
        "sections": sections,
        "quiz": quiz,
        "related_topics": sections[:5]
    }
    try:
        QuizOutput.parse_obj(output)
    except ValidationError:
        output = {
            "title": title,
            "summary": output.get("summary", ""),
            "key_entities": {"people": [], "organizations": [], "locations": []},
            "sections": sections,
            "quiz": output.get("quiz", []),
            "related_topics": output.get("related_topics", [])
        }
    return output
