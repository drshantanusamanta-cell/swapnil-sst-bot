"""
Web Content Fetcher
Fetches supplementary content from Indian education websites.
Uses web scraping with proper fallbacks.
"""

import requests
import re
import html
import streamlit as st

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


@st.cache_data(ttl=7200, show_spinner=False)
def fetch_edurev_content(topic: str) -> dict:
    """
    Attempt to fetch study notes from EduRev for a given topic.
    Returns formatted content or empty dict on failure.
    """
    search_url = f"https://www.google.com/search?q=site:edurev.in+{topic}+class+5+ICSE"
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            # Extract URLs from search results (simple regex approach)
            urls = re.findall(r'(https://edurev\.in/[^\s"&]+)', resp.text)
            if urls:
                return {"source": "EduRev", "url": urls[0], "note": "Visit EduRev for detailed notes on this topic."}
    except Exception:
        pass
    return {}


@st.cache_data(ttl=7200, show_spinner=False)
def fetch_supplementary_links(topic: str) -> list:
    """
    Search for supplementary learning resources related to a topic.
    Returns a list of resource dicts with title, url, and source.
    """
    search_query = f"ICSE class 5 {topic} study material notes"
    resources = []

    try:
        resp = requests.get(
            "https://www.google.com/search",
            headers=HEADERS,
            params={"q": search_query, "num": 5},
            timeout=10,
        )
        if resp.status_code == 200:
            # Extract search result titles and URLs
            results = re.findall(
                r'<a href="/url\?q=(https?://[^&]+)&[^"]*"[^>]*>(.*?)</a>',
                resp.text,
            )
            for url, title in results[:5]:
                title = html.unescape(re.sub(r"<[^>]+>", "", title))
                if title and len(title) > 15:
                    resources.append({"title": title, "url": url})
    except Exception:
        pass

    return resources


@st.cache_data(ttl=7200, show_spinner=False)
def search_education_videos(topic: str) -> list:
    """
    Search for educational YouTube videos related to a topic.
    Returns a list of video info dicts.
    """
    search_query = f"ICSE class 5 social studies {topic} explained for kids"
    videos = []

    try:
        resp = requests.get(
            "https://www.google.com/search",
            headers=HEADERS,
            params={
                "q": search_query,
                "num": 5,
                "tbm": "vid",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            video_results = re.findall(
                r'<a href="/url\?q=(https://www\.youtube\.com/watch\?v=[^&]+)&[^"]*"[^>]*>(.*?)</a>',
                resp.text,
            )
            for url, title in video_results[:3]:
                title = html.unescape(re.sub(r"<[^>]+>", "", title))
                if title and len(title) > 10:
                    videos.append({"title": title, "url": url})
    except Exception:
        pass

    return videos