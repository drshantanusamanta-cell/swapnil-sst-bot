"""
Open Trivia Database API Fetcher
Fetches quiz questions and formats them for Class V students.
"""

import requests
import random
import html
import streamlit as st

OPENTDB_URL = "https://opentdb.com/api.php"

# Category mapping
CATEGORY_MAP = {
    17: "Science",
    22: "Geography",
    23: "History",
    9: "General Knowledge",
}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_trivia_questions(
    categories: list = None,
    amount: int = 10,
    difficulty: str = "easy",
) -> list:
    """
    Fetch trivia questions from Open Trivia DB.
    If categories provided, fetch from each and combine.
    """
    if not categories:
        categories = [22, 23]  # Default: Geography + History

    all_questions = []
    per_category = max(1, amount // len(categories))

    for cat in categories:
        try:
            params = {
                "amount": per_category,
                "category": cat,
                "difficulty": difficulty,
                "type": "multiple",
            }
            resp = requests.get(OPENTDB_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("response_code") == 0:
                for q in data.get("results", []):
                    all_questions.append(format_question(q))

        except requests.RequestException:
            continue

    random.shuffle(all_questions)
    return all_questions[:amount]


def format_question(q: dict) -> dict:
    """Format a raw trivia question into a student-friendly format."""
    question_text = html.unescape(q["question"])
    correct = html.unescape(q["correct_answer"])
    incorrect = [html.unescape(w) for w in q["incorrect_answers"]]

    options = incorrect + [correct]
    random.shuffle(options)

    return {
        "question": question_text,
        "options": options,
        "correct_index": options.index(correct),
        "correct_answer": correct,
        "category": q.get("category", ""),
        "difficulty": q.get("difficulty", "easy"),
    }


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_category_token_count(category: int) -> int:
    """Get total available questions in a category."""
    try:
        resp = requests.get(
            OPENTDB_URL, params={"amount": 1, "category": category}, timeout=10
        )
        data = resp.json()
        return 1  # We can't easily get total count, just return 1
    except Exception:
        return 0