import requests
import streamlit as st

# ---- Settings ----------------------------------------------------------
BUSINESS = "a car insurance company"
LABELS = ["price", "coverage", "quality of service", "other"]
GUIDE = """Label the comment with exactly one of: price, coverage, quality of service, or other.
If more than one feature of the service is mentioned, label by the first mentioned."""
MODEL = "openai/gpt-oss-20b"
URL = "https://api.groq.com/openai/v1/chat/completions"

# Small safety net: if the LLM returns a near-match, map it to a valid label.
ALIASES = {
    "service": "quality of service",
    "customer service": "quality of service",
    "quality": "quality of service",
    "cost": "price",
    "premium": "price",
    "pricing": "price",
    "cover": "coverage",
}
# ------------------------------------------------------------------------


def label_comment(text):
    key = st.secrets["GROQ_API_KEY"]
    prompt = f"You label customer comments for {BUSINESS}.\n{GUIDE}\n\nComment: {text}"
    response = requests.post(
        URL,
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": MODEL,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    label = answer.strip().lower().strip(" .")
    if label in LABELS:
        return label
    if label in ALIASES:
        return ALIASES[label]
    return "other"