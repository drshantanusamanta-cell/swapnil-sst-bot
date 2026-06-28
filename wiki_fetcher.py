"""
Wikipedia API Content Fetcher
Fetches, simplifies, and formats Wikipedia content for Class V students.
"""

import requests
import html
import re
import streamlit as st


WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

HEADERS = {
    "User-Agent": "SST-Tutor/1.0 (Educational Streamlit App for ICSE Class V; contact: github.com/user)",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_wikipedia_page(query: str) -> dict:
    """Fetch a Wikipedia page by search query. Returns parsed content."""
    # Step 1: Search for the best matching page
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 1,
        "format": "json",
    }
    try:
        resp = requests.get(WIKI_API, params=search_params, timeout=10, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("query", {}).get("search", [])

        if not results:
            return {"found": False, "query": query}

        page_title = results[0]["title"]

        # Step 2: Get the page content (extracts + summary)
        content_params = {
            "action": "query",
            "prop": "extracts|pageimages|info",
            "exintro": 1,
            "explaintext": 1,
            "exsectionformat": "plain",
            "piprop": "thumbnail",
            "pithumbsize": 600,
            "inprop": "url",
            "titles": page_title,
            "format": "json",
        }
        resp2 = requests.get(WIKI_API, params=content_params, timeout=10, headers=HEADERS)
        resp2.raise_for_status()
        data2 = resp2.json()

        pages = data2.get("query", {}).get("pages", {})
        page = list(pages.values())[0]

        extract = page.get("extract", "")
        thumbnail = page.get("thumbnail", {})
        image_url = thumbnail.get("source", "") if thumbnail else ""
        full_url = page.get("fullurl", "")

        # Step 3: Get the summary (REST API - cleaner)
        summary = ""
        try:
            summary_resp = requests.get(
                WIKI_SUMMARY_URL.format(title=page_title.replace(" ", "_")),
                timeout=10,
                headers=HEADERS,
            )
            if summary_resp.status_code == 200:
                summary_data = summary_resp.json()
                summary = summary_data.get("extract", "")
        except Exception:
            summary = extract[:500] if extract else ""

        # Step 4: Format the content for a 10-year-old student
        formatted = simplify_for_students(extract)

        return {
            "found": True,
            "title": page_title,
            "summary": summary,
            "content": formatted,
            "image_url": image_url,
            "wiki_url": full_url,
            "query": query,
        }

    except requests.RequestException as e:
        return {"found": False, "query": query, "error": str(e)}


def simplify_for_students(text: str) -> str:
    """
    Simplify Wikipedia content for Class V students.
    Cleans up references, removes overly complex sections.
    """
    if not text:
        return ""

    # Remove Wikipedia-specific formatting
    text = re.sub(r"\[edit\]", "", text)
    text = re.sub(r"\[\d+\]", "", text)  # Remove citation numbers
    text = re.sub(r"\*+", "", text)  # Remove bullet markers (keep the text)

    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # Limit to first ~2000 characters (enough for a student to read)
    if len(text) > 2000:
        # Try to cut at a paragraph boundary
        paragraphs = text.split("\n\n")
        result = []
        total_len = 0
        for p in paragraphs:
            if total_len + len(p) > 2000:
                break
            result.append(p)
            total_len += len(p)
        text = "\n\n".join(result)
        if total_len < 500:
            text = text[:2000]

    return text


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_multiple_wiki_pages(queries: list) -> list:
    """Fetch content for multiple queries and return all successful results."""
    results = []
    for query in queries:
        result = fetch_wikipedia_page(query)
        if result.get("found"):
            results.append(result)
    return results


def get_related_images(query: str) -> list:
    """Search for images related to a topic via Wikipedia's image search."""
    params = {
        "action": "query",
        "list": "images",
        "titles": query,
        "imlimit": 5,
        "format": "json",
    }
    try:
        resp = requests.get(WIKI_API, params=params, timeout=10, headers=HEADERS)
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        if pages:
            page = list(pages.values())[0]
            images = page.get("images", [])
            return [
                img["title"]
                for img in images
                if not any(
                    skip in img["title"].lower()
                    for skip in ["icon", "logo", "flag", "symbol", "commons-logo", "edit"]
                )
            ][:3]
    except Exception:
        pass
    return []