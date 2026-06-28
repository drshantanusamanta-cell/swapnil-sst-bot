"""
ICSE Class V Social Studies - Interactive Tutor
==============================================
A hybrid Streamlit app that combines:
  1. Wikipedia API  - rich encyclopedic content
  2. Open Trivia DB - fun quiz questions
  3. Web Sources    - supplementary Indian education resources

Deploy to Streamlit Community Cloud:
  https://share.streamlit.io/
"""

import streamlit as st
import random
import json
import time
import base64
import csv
import io
from datetime import datetime

# Page config - must be the first Streamlit command
st.set_page_config(
    page_title="SST Tutor - ICSE Class V",
    page_icon="\U0001f4da",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import modules ────────────────────────────────────────────────────────
from chapters import CHAPTERS, get_all_chapters, get_chapter, get_sections, TRIVIA_CATEGORY_MAP
from wiki_fetcher import fetch_wikipedia_page, fetch_multiple_wiki_pages, get_related_images
from trivia_fetcher import fetch_trivia_questions, CATEGORY_MAP
from web_fetcher import fetch_supplementary_links, search_education_videos


# ── Session State Initialization ───────────────────────────────────────────
def init_session_state():
    defaults = {
        "current_chapter": None,
        "current_section": None,
        "mode": "learn",
        "quiz_questions": [],
        "quiz_index": 0,
        "quiz_score": 0,
        "quiz_answered": False,
        "selected_option": None,
        "quiz_complete": False,
        "progress": {},
        "show_answer": False,
        "wiki_content": {},
        "expanded_concept": None,
        "dark_mode": False,
        "bookmarks": [],  # list of chapter_key strings
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ── Dark Mode CSS ─────────────────────────────────────────────────────────
DARK_MODE_CSS = """
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
.block-container {
    background: #0f0f1a !important;
    color: #e0e0e0 !important;
}
.stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown li {
    color: #e0e0e0 !important;
}
.stMetricLabel {
    color: #90a4ae !important;
}
.stMetricValue {
    color: #e0e0e0 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a2e;
}
.stTabs [data-baseweb="tab"] {
    color: #90a4ae;
}
.stTabs [aria-selected="true"] {
    color: #82b1ff !important;
    background: #1a1a2e !important;
}
.stExpander {
    background: #1a1a2e !important;
    border-color: #333 !important;
}
div[data-testid="stExpander"] details {
    background: #1a1a2e;
    border: 1px solid #333;
}
div[data-testid="stExpander"] summary {
    color: #e0e0e0;
}
div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] {
    color: #e0e0e0;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, #7c4dff, #448aff) !important;
}
.stButton > button {
    background: #1a1a2e !important;
    color: #e0e0e0 !important;
    border-color: #444 !important;
}
.stButton > button:hover {
    border-color: #7c4dff !important;
    background: #2a2a4e !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: #5c6bc0 !important;
    color: #fff !important;
    border-color: #5c6bc0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border-color: #333 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2a2a4e !important;
    border-color: #7c4dff !important;
}
/* Dark mode specific component overrides */
.dark-card {
    background: #1a1a2e !important;
    border-color: #333 !important;
}
.dark-fun-fact {
    background: linear-gradient(135deg, #1a237e, #283593) !important;
    border-left-color: #ffd54f !important;
}
.dark-question-card {
    background: #1a1a2e !important;
    border-color: #333 !important;
}
.dark-concept-header {
    background: linear-gradient(135deg, #1a237e, #283593) !important;
}
.dark-discuss-header {
    background: linear-gradient(135deg, #3e2723, #4e342e) !important;
}
.dark-discuss-q {
    background: #1a1a2e !important;
}
.dark-tip-box {
    background: #1b3a1b !important;
}
.stAlert {
    background: #1a1a2e !important;
    color: #e0e0e0 !important;
}
.stSuccess {
    background: #1b3a1b !important;
    border-left-color: #4caf50 !important;
    color: #a5d6a7 !important;
}
.stWarning {
    background: #3e2723 !important;
    color: #ffcc80 !important;
}
.stInfo {
    background: #1a237e !important;
    color: #90caf9 !important;
}
.stError {
    background: #3e1212 !important;
    color: #ef9a9a !important;
}
hr {
    border-color: #333 !important;
}
"""

LIGHT_MODE_CSS = """
/* Main theme overrides */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Chapter cards in sidebar */
.chapter-card {
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}
.chapter-card:hover {
    background: #e8f4fd;
    border-color: #2196F3;
    transform: translateX(4px);
}
.chapter-card.active {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    border-color: #1976D2;
    box-shadow: 0 2px 8px rgba(33,150,243,0.2);
}

/* Section headers */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
    padding-bottom: 4px;
    border-bottom: 2px solid;
}

/* Fun fact box */
.fun-fact-box {
    background: linear-gradient(135deg, #fff9c4, #fff176);
    border-left: 4px solid #f9a825;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 10px 0;
}

/* Key concept pills */
.concept-pill {
    display: inline-block;
    background: #e3f2fd;
    border-radius: 20px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 0.9rem;
    border: 1px solid #90caf9;
}

/* Quiz option buttons */
.stButton > button {
    width: 100%;
    text-align: left;
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 1rem;
    margin-bottom: 8px;
    border: 2px solid #e0e0e0;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: #2196F3;
    background: #e3f2fd;
}

/* Score badge */
.score-badge {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Progress bar styling */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 10px;
}

/* Wikipedia image */
.wiki-image {
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    margin: 10px 0;
}

/* Hide Streamlit defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
"""


def inject_css():
    """Inject CSS based on current theme."""
    if st.session_state.dark_mode:
        st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_MODE_CSS, unsafe_allow_html=True)


inject_css()


# ── Theme Helper ──────────────────────────────────────────────────────────
def thm():
    """Return theme-dependent color tokens."""
    if st.session_state.dark_mode:
        return {
            "bg": "#1a1a2e",
            "bg2": "#16213e",
            "fg": "#e0e0e0",
            "muted": "#90a4ae",
            "card": "#1a1a2e",
            "border": "#333",
            "primary": "#82b1ff",
            "success": "#a5d6a7",
            "warning": "#ffcc80",
            "error": "#ef9a9a",
            "link": "#82b1ff",
            "accent": "#7c4dff",
            "gradient1": "#1a237e",
            "gradient2": "#283593",
            "fun_bg": "linear-gradient(135deg, #1a237e, #283593)",
            "fun_border": "#ffd54f",
            "concept_bg": "linear-gradient(135deg, #1a237e, #283593)",
            "discuss_bg": "linear-gradient(135deg, #3e2723, #4e342e)",
            "discuss_q_bg": "#1a1a2e",
            "tip_bg": "#1b3a1b",
            "score_bg": "#1b3a1b",
            "score_fg": "#66bb6a",
            "q_card_bg": "#1a1a2e",
            "q_card_border": "#444",
            "opt_bg": "#1a1a2e",
            "opt_border": "#444",
            "correct_bg": "#1b3a1b",
            "correct_border": "#4caf50",
            "wrong_bg": "#3e1212",
            "wrong_border": "#ef5350",
            "neutral_bg": "#222",
            "neutral_border": "#444",
        }
    else:
        return {
            "bg": "#ffffff",
            "bg2": "#f5f5f5",
            "fg": "#37474f",
            "muted": "#90a4ae",
            "card": "#ffffff",
            "border": "#e0e0e0",
            "primary": "#1565C0",
            "success": "#2e7d32",
            "warning": "#e65100",
            "error": "#c62828",
            "link": "#1976D2",
            "accent": "#667eea",
            "gradient1": "#e3f2fd",
            "gradient2": "#bbdefb",
            "fun_bg": "linear-gradient(135deg, #fff9c4, #fff176)",
            "fun_border": "#f9a825",
            "concept_bg": "linear-gradient(135deg, #e3f2fd, #bbdefb)",
            "discuss_bg": "linear-gradient(135deg, #fff3e0, #ffe0b2)",
            "discuss_q_bg": "#ffffff",
            "tip_bg": "#e8f5e9",
            "score_bg": "#e8f5e9",
            "score_fg": "#66bb6a",
            "q_card_bg": "#ffffff",
            "q_card_border": "#e0e0e0",
            "opt_bg": "#f5f5f5",
            "opt_border": "#e0e0e0",
            "correct_bg": "#e8f5e9",
            "correct_border": "#43a047",
            "wrong_bg": "#ffebee",
            "wrong_border": "#ef5350",
            "neutral_bg": "#f5f5f5",
            "neutral_border": "#e0e0e0",
        }


# ── Helper Functions ───────────────────────────────────────────────────────
def chapter_key(section, num):
    return f"{section}_{num}"


def mark_chapter_read(section, num):
    key = chapter_key(section, num)
    if key not in st.session_state.progress:
        st.session_state.progress[key] = {"read": False, "quiz_score": 0, "quiz_total": 0}
    st.session_state.progress[key]["read"] = True


def update_quiz_score(section, num, score, total):
    key = chapter_key(section, num)
    if key not in st.session_state.progress:
        st.session_state.progress[key] = {"read": False, "quiz_score": 0, "quiz_total": 0}
    st.session_state.progress[key]["quiz_score"] = max(
        st.session_state.progress[key]["quiz_score"], score
    )
    st.session_state.progress[key]["quiz_total"] = max(
        st.session_state.progress[key]["quiz_total"], total
    )


def get_progress_pct():
    """Calculate overall progress percentage."""
    total = 0
    completed = 0
    for section in get_sections():
        for ch in CHAPTERS[section]:
            total += 1
            key = chapter_key(section, ch["num"])
            if st.session_state.progress.get(key, {}).get("read", False):
                completed += 1
    return (completed / total * 100) if total > 0 else 0


def toggle_bookmark(section, num):
    """Toggle bookmark for a chapter."""
    key = chapter_key(section, num)
    if key in st.session_state.bookmarks:
        st.session_state.bookmarks.remove(key)
    else:
        st.session_state.bookmarks.append(key)


def is_bookmarked(section, num):
    return chapter_key(section, num) in st.session_state.bookmarks


def get_bookmark_label(section, num):
    return "\U0001f516" if is_bookmarked(section, num) else "\U0001f517"


# ── Export Progress ───────────────────────────────────────────────────────
def get_full_progress_data():
    """Build a complete progress report as a list of dicts."""
    report = []
    for section in get_sections():
        for ch in CHAPTERS[section]:
            key = chapter_key(section, ch["num"])
            info = st.session_state.progress.get(key, {})
            report.append({
                "Section": section,
                "Chapter": ch["num"],
                "Title": ch["title"],
                "Read": "Yes" if info.get("read", False) else "No",
                "Quiz Score": info.get("quiz_score", 0),
                "Quiz Total": info.get("quiz_total", 0),
                "Quiz %": round(
                    (info.get("quiz_score", 0) / info.get("quiz_total", 1) * 100)
                    if info.get("quiz_total", 0) > 0 else 0, 1
                ),
                "Bookmarked": "Yes" if key in st.session_state.bookmarks else "No",
            })
    return report


def export_progress_json():
    """Return a downloadable JSON of the progress report."""
    data = {
        "app": "SST Tutor - ICSE Class V",
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_progress_pct": round(get_progress_pct(), 1),
        "chapters_completed": sum(
            1 for r in get_full_progress_data() if r["Read"] == "Yes"
        ),
        "total_chapters": sum(len(CHAPTERS[s]) for s in get_sections()),
        "bookmarked_chapters": len(st.session_state.bookmarks),
        "chapter_details": get_full_progress_data(),
    }
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    b64 = base64.b64encode(json_bytes).decode()
    href = f"data:application/json;base64,{b64}"
    filename = f"sst-progress-{datetime.now().strftime('%Y%m%d')}.json"
    return href, filename


def export_progress_csv():
    """Return a downloadable CSV of the progress report."""
    report = get_full_progress_data()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=report[0].keys())
    writer.writeheader()
    writer.writerows(report)
    csv_bytes = output.getvalue().encode("utf-8")
    b64 = base64.b64encode(csv_bytes).decode()
    href = f"data:text/csv;base64,{b64}"
    filename = f"sst-progress-{datetime.now().strftime('%Y%m%d')}.csv"
    return href, filename


def render_export_buttons():
    """Render JSON and CSV download buttons."""
    json_href, json_fn = export_progress_json()
    csv_href, csv_fn = export_progress_csv()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<a href="{json_href}" download="{json_fn}" style="text-decoration:none;">'
            f'<button style="width:100%;padding:10px;border-radius:10px;border:2px solid #667eea;'
            f'background:transparent;color:inherit;cursor:pointer;font-size:0.95rem;font-weight:600;">'
            f'\U0001f4c4 Export as JSON</button></a>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<a href="{csv_href}" download="{csv_fn}" style="text-decoration:none;">'
            f'<button style="width:100%;padding:10px;border-radius:10px;border:2px solid #667eea;'
            f'background:transparent;color:inherit;cursor:pointer;font-size:0.95rem;font-weight:600;">'
            f'\U0001f4ca Export as CSV</button></a>',
            unsafe_allow_html=True,
        )


# ── Home Screen ────────────────────────────────────────────────────────────
def render_home():
    """Render the welcome / home screen."""
    t = thm()

    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, {t['accent']}, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                \U0001f4da SST Tutor
            </h1>
            <h2 style="color: {t['muted']};">ICSE Class V - Social Studies</h2>
            <p style="color: {t['muted']}; font-size: 1.1rem;">Your Interactive Learning Companion</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    learn_bg = "linear-gradient(135deg, #1a237e, #283593)" if st.session_state.dark_mode else "linear-gradient(135deg, #e3f2fd, #bbdefb)"
    quiz_bg = "linear-gradient(135deg, #1b3a1b, #2e4a2e)" if st.session_state.dark_mode else "linear-gradient(135deg, #e8f5e9, #c8e6c9)"
    explore_bg = "linear-gradient(135deg, #3e2723, #4e342e)" if st.session_state.dark_mode else "linear-gradient(135deg, #fff3e0, #ffe0b2)"

    with col1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem; background: {learn_bg}; border-radius: 16px; min-height: 180px;">
                <div style="font-size: 3rem;">\U0001f30d</div>
                <h3 style="color: {t['primary'] if st.session_state.dark_mode else '#1565C0'};">Learn</h3>
                <p style="color: {t['muted']};">Read & explore chapters with rich content from Wikipedia</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem; background: {quiz_bg}; border-radius: 16px; min-height: 180px;">
                <div style="font-size: 3rem;">\U0001f9e0</div>
                <h3 style="color: {t['success']};">Quiz</h3>
                <p style="color: {t['muted']};">Test your knowledge with fun trivia questions</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem; background: {explore_bg}; border-radius: 16px; min-height: 180px;">
                <div style="font-size: 3rem;">\U0001f50d</div>
                <h3 style="color: {t['warning']};">Explore</h3>
                <p style="color: {t['muted']};">Discover videos, links, and more resources</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Quick stats
    st.markdown("---")
    pct = get_progress_pct()
    total_chapters = sum(len(CHAPTERS[s]) for s in get_sections())
    read_count = sum(
        1 for s in get_sections()
        for ch in CHAPTERS[s]
        if st.session_state.progress.get(chapter_key(s, ch["num"]), {}).get("read", False)
    )
    bookmark_count = len(st.session_state.bookmarks)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Chapters Available", total_chapters)
    col2.metric("Chapters Read", read_count)
    col3.metric("Bookmarked", bookmark_count)
    col4.metric("Overall Progress", f"{pct:.0f}%")
    st.progress(pct / 100)

    # Export section
    st.markdown("---")
    st.markdown(f"**\U0001f4e5 Export Your Progress**")
    render_export_buttons()

    # Bookmarks quick access
    if st.session_state.bookmarks:
        st.markdown("---")
        st.markdown(f"**\U0001f516 Your Bookmarked Chapters**")
        bookmark_cols = st.columns(min(len(st.session_state.bookmarks), 3))
        for i, bk in enumerate(st.session_state.bookmarks):
            section, num = bk.rsplit("_", 1)
            num = int(num)
            ch = get_chapter(section, num)
            if ch:
                with bookmark_cols[i % len(bookmark_cols)]:
                    if st.button(
                        f"{ch['emoji']} {ch['title']}",
                        key=f"bk_home_{bk}",
                        use_container_width=True,
                    ):
                        st.session_state.current_section = section
                        st.session_state.current_chapter = num
                        st.session_state.mode = "learn"
                        st.session_state.quiz_questions = []
                        st.rerun()

    st.markdown(
        f"""
        ---
        <div style="text-align: center; color: {t['muted']};">
            <p>\U0001f4a1 <strong>How to use:</strong> Pick a chapter from the sidebar, choose Learn / Quiz / Explore, bookmark your favourites, and export progress anytime!</p>
            <p>\U0001f3af <strong>Tips:</strong> Read each chapter first, then take the quiz. Bookmark chapters you want to revisit!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Learn Mode ─────────────────────────────────────────────────────────────
def render_learn_mode(chapter):
    """Render the learning mode with Wikipedia content + key concepts."""
    t = thm()

    st.markdown(
        f"""<h2 style="color: {t['primary']};">{chapter['emoji']} {chapter['title']}</h2>
        <p style="color: {t['muted']};">{chapter['section']} \u00b7 Chapter {chapter['num']}</p>""",
        unsafe_allow_html=True,
    )

    # Bookmark + Mark Read row
    bk_label = "\U0001f516 Remove Bookmark" if is_bookmarked(chapter["section"], chapter["num"]) else "\U0001f517 Bookmark This Chapter"
    col_bk, col_spacer, col_read = st.columns([1, 1, 1])
    with col_bk:
        if st.button(bk_label, key="bookmark_btn", use_container_width=True):
            toggle_bookmark(chapter["section"], chapter["num"])
            st.rerun()
    with col_read:
        if st.button("\u2705 Mark Chapter as Read", key="mark_read_btn", use_container_width=True):
            mark_chapter_read(chapter["section"], chapter["num"])
            st.success("Chapter marked as read! Great progress!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    learn_tab1, learn_tab2, learn_tab3 = st.tabs([
        "\U0001f4d6 Key Concepts",
        "\U0001f30d Wikipedia Deep Dive",
        "\U0001f4cb Discussion Questions",
    ])

    # Tab 1: Key Concepts
    with learn_tab1:
        st.markdown(
            f'<div style="background: {t["concept_bg"]}; padding: 18px; border-radius: 12px; margin-bottom: 16px;">'
            f'<h4 style="color: {t["primary"]}; margin: 0;">\U0001f511 Key Concepts to Remember</h4>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for i, concept in enumerate(chapter["key_concepts"], 1):
            parts = concept.split(" \u2014 ")
            term = parts[0]
            definition = parts[1] if len(parts) > 1 else ""

            with st.expander(f"\U0001f4cc {term}", expanded=(i <= 3)):
                if definition:
                    st.markdown(f"**{term}** \u2014 {definition}")
                else:
                    st.markdown(concept)

        if chapter.get("fun_fact"):
            st.markdown(
                f'<div style="background: {t["fun_bg"]}; border-left: 4px solid {t["fun_border"]};'
                f' border-radius: 8px; padding: 14px 18px; margin: 10px 0;">'
                f'<strong>\u2b50 Fun Fact!</strong><br>{chapter["fun_fact"]}</div>',
                unsafe_allow_html=True,
            )

    # Tab 2: Wikipedia Deep Dive
    with learn_tab2:
        st.markdown(
            f'<div style="background: {t["bg2"]}; padding: 12px 18px; border-radius: 10px; margin-bottom: 14px;">'
            f'<p style="margin:0; color: {t["muted"]};">\U0001f310 Content fetched live from Wikipedia</p></div>',
            unsafe_allow_html=True,
        )

        queries = chapter["wiki_queries"][:3]
        with st.spinner("\U0001f50d Searching Wikipedia for you..."):
            wiki_results = fetch_multiple_wiki_pages(queries)

        if wiki_results:
            main = wiki_results[0]
            col_img, col_text = st.columns([1, 2])
            with col_img:
                if main.get("image_url"):
                    st.image(main["image_url"], use_column_width=True)
                else:
                    st.markdown(
                        f'<div style="text-align:center; font-size:4rem; padding:2rem;">{chapter["emoji"]}</div>',
                        unsafe_allow_html=True,
                    )
            with col_text:
                st.markdown(f"#### From Wikipedia: {main['title']}")
                st.markdown(main.get("summary", ""))
                if main.get("wiki_url"):
                    st.markdown(f"\U0001f517 [Read full article on Wikipedia]({main['wiki_url']})")

            if len(wiki_results) > 1:
                st.markdown("---")
                st.markdown("**\U0001f504 More Resources:**")
                for extra in wiki_results[1:]:
                    with st.expander(f"\U0001f4d0 {extra['title']}"):
                        st.markdown(extra.get("summary", "No summary available."))
                        st.markdown(extra.get("content", ""))
                        if extra.get("wiki_url"):
                            st.markdown(f"\U0001f517 [Read on Wikipedia]({extra['wiki_url']})")
        else:
            st.warning("\U0001f614 Could not fetch content from Wikipedia right now. Try the Key Concepts tab above!")
            st.info("\U0001f4a1 Tip: You can also check your internet connection and try again.")

    # Tab 3: Discussion Questions
    with learn_tab3:
        st.markdown(
            f'<div style="background: {t["discuss_bg"]}; padding: 18px; border-radius: 12px; margin-bottom: 16px;">'
            f'<h4 style="color: {t["warning"]}; margin: 0;">\U0001f4ac Think & Discuss</h4>'
            f'<p style="color: {t["muted"]}; margin: 4px 0 0 0;">Try answering these questions. Discuss with your parents or teacher!</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for i, q in enumerate(chapter.get("discussion_questions", []), 1):
            st.markdown(
                f'<div style="background: {t["discuss_q_bg"]}; padding: 14px 18px; border-radius: 10px;'
                f' border-left: 4px solid #ff9800; margin-bottom: 10px;">'
                f'<strong>Q{i}.</strong> {q}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div style="background: {t["tip_bg"]}; padding: 14px 18px; border-radius: 10px; margin-top: 16px;">'
            f'<strong>\U0001f4ac Discussion Tip:</strong> Try to answer in your own words. If you\'re not sure, go back to the Key Concepts tab and read again!</div>',
            unsafe_allow_html=True,
        )


# ── Quiz Mode ──────────────────────────────────────────────────────────────
def render_quiz_mode(chapter):
    """Render the quiz mode with trivia questions."""
    t = thm()

    st.markdown(
        f"""<h2 style="color: {t['success']};">\U0001f9e0 Quiz Time!</h2>
        <p style="color: {t['muted']};">{chapter['emoji']} {chapter['title']} \u00b7 {chapter['section']} \u00b7 Chapter {chapter['num']}</p>""",
        unsafe_allow_html=True,
    )

    if not st.session_state.quiz_questions:
        categories = chapter.get("trivia_categories", [22, 23])
        with st.spinner("\U0001f50d Fetching quiz questions..."):
            questions = fetch_trivia_questions(categories=categories, amount=5, difficulty="easy")
        if not questions:
            questions = generate_concept_quiz(chapter)
        st.session_state.quiz_questions = questions
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_complete = False

    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index
    total = len(questions)

    if st.session_state.quiz_complete or idx >= total:
        score = st.session_state.quiz_score
        pct = (score / total * 100) if total > 0 else 0
        update_quiz_score(chapter["section"], chapter["num"], score, total)

        if pct >= 80:
            emoji, msg, color = "\U0001f3c6", "Excellent! You're a star student!", "#2e7d32"
        elif pct >= 60:
            emoji, msg, color = "\U0001f44d", "Good job! Keep learning!", "#f9a825"
        elif pct >= 40:
            emoji, msg, color = "\U0001f4aa", "Nice try! Review the chapter and try again.", "#e65100"
        else:
            emoji, msg, color = "\U0001f4da", "Don't worry! Go through the chapter again and come back stronger.", "#c62828"

        st.markdown(
            f'<div style="text-align: center; padding: 2rem;">'
            f'<div style="font-size: 4rem;">{emoji}</div>'
            f'<h2 style="color: {color};">Quiz Complete!</h2>'
            f'<div class="score-badge">{score} / {total}</div>'
            f'<p style="font-size: 1.2rem; color: {color};">{msg}</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("**\U0001f4cb Answer Review:**")
        for i, q in enumerate(questions, 1):
            with st.expander(f"Q{i}: {q['question']}"):
                st.success(f"\u2705 **Correct Answer:** {q['correct_answer']}")

        col_retake, col_export = st.columns(2)
        with col_retake:
            if st.button("\U0001f504 Retake Quiz", key="retake_btn", use_container_width=True):
                st.session_state.quiz_questions = []
                st.rerun()
        with col_export:
            st.markdown(
                '<span style="opacity:0.5; font-size:0.9rem; padding: 12px 0; display:inline-block;">\U0001f4e5 Export progress from Home</span>'
            )

    else:
        q = questions[idx]
        progress_val = (idx + 1) / total
        st.progress(progress_val, text=f"Question {idx + 1} of {total}")

        col_score, col_qnum = st.columns([1, 3])
        with col_score:
            st.markdown(
                f'<div style="text-align: center; background: {t["score_bg"]}; padding: 10px; border-radius: 10px;">'
                f'<div style="font-size: 0.85rem; color: {t["score_fg"]};">SCORE</div>'
                f'<div class="score-badge">{st.session_state.quiz_score}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div style="background: {t["q_card_bg"]}; padding: 20px; border-radius: 14px;'
            f' border: 2px solid {t["q_card_border"]}; margin: 10px 0;">'
            f'<p style="font-size: 1.2rem; font-weight: 600; color: {t["fg"]};">{q["question"]}</p></div>',
            unsafe_allow_html=True,
        )

        if not st.session_state.quiz_answered:
            for i, opt in enumerate(q["options"]):
                if st.button(opt, key=f"opt_{idx}_{i}", use_container_width=True):
                    st.session_state.selected_option = i
                    st.session_state.quiz_answered = True
                    if i == q["correct_index"]:
                        st.session_state.quiz_score += 1
                    st.rerun()
        else:
            selected = st.session_state.selected_option
            is_correct = selected == q["correct_index"]

            for i, opt in enumerate(q["options"]):
                if i == q["correct_index"]:
                    bg = t["correct_bg"] if not (is_correct and i == selected) else t["correct_bg"]
                    border = t["correct_border"]
                    icon = "\u2705 " if i == selected else "\u2714\ufe0f "
                elif i == selected and not is_correct:
                    bg, border, icon = t["wrong_bg"], t["wrong_border"], "\u274c "
                else:
                    bg, border, icon = t["neutral_bg"], t["neutral_border"], ""

                st.markdown(
                    f'<div style="padding: 12px 18px; border-radius: 10px; margin-bottom: 6px;'
                    f' background: {bg}; border: 2px solid {border};">'
                    f'{icon}{opt}</div>',
                    unsafe_allow_html=True,
                )

            if is_correct:
                st.success("\U0001f389 Correct! Well done!")
            else:
                st.error(f"\U0001f614 Not quite! The correct answer is: **{q['correct_answer']}**")

            if st.button("\u27a1\ufe0f Next Question", key="next_q_btn", use_container_width=True):
                st.session_state.quiz_index += 1
                st.session_state.quiz_answered = False
                st.session_state.selected_option = None
                st.rerun()


def generate_concept_quiz(chapter):
    """Generate quiz questions from key concepts when API fails."""
    questions = []
    concepts = chapter.get("key_concepts", [])
    random.shuffle(concepts)

    for concept in concepts[:5]:
        parts = concept.split(" \u2014 ")
        if len(parts) >= 2:
            term = parts[0]
            answer = parts[1]
            question_text = f"What is {term}?"
            wrong = []
            for other_concept in concepts:
                other_parts = other_concept.split(" \u2014 ")
                if len(other_parts) >= 2 and other_parts[0] != term:
                    wrong.append(other_parts[1][:60])
                if len(wrong) >= 3:
                    break
            while len(wrong) < 3:
                wrong.append("None of the above")
            wrong = wrong[:3]
            options = wrong + [answer]
            random.shuffle(options)
            questions.append({
                "question": question_text,
                "options": options,
                "correct_index": options.index(answer),
                "correct_answer": answer,
                "category": "ICSE",
                "difficulty": "easy",
            })
    return questions


# ── Explore Mode ───────────────────────────────────────────────────────────
def render_explore_mode(chapter):
    """Render the explore mode with supplementary resources."""
    t = thm()

    st.markdown(
        f"""<h2 style="color: {t['warning']};">\U0001f50d Explore More</h2>
        <p style="color: {t['muted']};">{chapter['emoji']} {chapter['title']} \u00b7 {chapter['section']} \u00b7 Chapter {chapter['num']}</p>""",
        unsafe_allow_html=True,
    )

    tab_links, tab_videos, tab_all_topics = st.tabs([
        "\U0001f517 Study Links",
        "\U0001f3ac Videos",
        "\U0001f4ca All Topics",
    ])

    with tab_links:
        st.markdown(
            f'<div style="background: {t["bg2"]}; padding: 12px 18px; border-radius: 10px; margin-bottom: 14px;">'
            f'<p style="margin:0; color: {t["muted"]};">\U0001f310 Searching the web for study resources...</p></div>',
            unsafe_allow_html=True,
        )
        with st.spinner("\U0001f50d Finding the best resources..."):
            links = fetch_supplementary_links(chapter["title"])
        if links:
            for i, link in enumerate(links, 1):
                st.markdown(
                    f'<div style="background: {t["card"]}; padding: 14px 18px; border-radius: 10px;'
                    f' border-left: 4px solid #2196F3; margin-bottom: 8px;">'
                    f'<strong>{i}.</strong> <a href="{link["url"]}" target="_blank" style="color:{t["link"]};">{link["title"]}</a></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("\U0001f4a1 No specific links found. Try searching on Google for more resources!")

        search_query = f"ICSE Class 5 {chapter['title']} study material"
        st.markdown(
            f'<div style="background: {t["bg2"]}; padding: 14px 18px; border-radius: 10px; margin-top: 12px;">'
            f'<strong>\U0001f50d Search yourself:</strong><br>'
            f'<a href="https://www.google.com/search?q={search_query}" target="_blank" style="color:{t["link"]};">'
            f'\U0001f310 Google: {search_query}</a></div>',
            unsafe_allow_html=True,
        )

    with tab_videos:
        st.markdown(
            f'<div style="background: {t["bg2"]}; padding: 12px 18px; border-radius: 10px; margin-bottom: 14px;">'
            f'<p style="margin:0; color: {t["muted"]};">\U0001f3ac Looking for educational videos...</p></div>',
            unsafe_allow_html=True,
        )
        with st.spinner("\U0001f50d Searching for videos..."):
            videos = search_education_videos(chapter["title"])
        if videos:
            for i, vid in enumerate(videos, 1):
                st.markdown(
                    f'<div style="background: {t["card"]}; padding: 14px 18px; border-radius: 10px;'
                    f' border-left: 4px solid #f44336; margin-bottom: 8px;">'
                    f'<strong>{i}.</strong> \U0001f3ac <a href="{vid["url"]}" target="_blank" style="color:{t["link"]};">{vid["title"]}</a></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("\U0001f4a1 No videos found automatically. Try searching YouTube!")

        yt_query = f"ICSE Class 5 Social Studies {chapter['title']}"
        st.markdown(
            f'<div style="background: {t["bg2"]}; padding: 14px 18px; border-radius: 10px; margin-top: 12px;">'
            f'<strong>\U0001f3ac Search YouTube:</strong><br>'
            f'<a href="https://www.youtube.com/results?search_query={yt_query}" target="_blank" style="color:{t["link"]};">'
            f'\U0001f3ac YouTube: {yt_query}</a></div>',
            unsafe_allow_html=True,
        )

    with tab_all_topics:
        st.markdown(
            f'<div style="background: {t["bg2"]}; padding: 18px; border-radius: 12px; margin-bottom: 16px;">'
            f'<h4 style="color: {t["primary"]}; margin: 0;">\U0001f4cb Topics in This Chapter</h4>'
            f'<p style="color: {t["muted"]}; margin: 4px 0 0 0;">All Wikipedia topics covered for this chapter</p></div>',
            unsafe_allow_html=True,
        )
        for i, query in enumerate(chapter["wiki_queries"], 1):
            wiki_link = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
            row_bg = t["bg2"] if i % 2 == 1 else t["card"]
            st.markdown(
                f'<div style="padding: 10px 18px; margin-bottom: 4px; border-radius: 8px; background: {row_bg};">'
                f'<strong>{i}.</strong> <a href="{wiki_link}" target="_blank" style="color:{t["link"]};">\U0001f30d {query}</a></div>',
                unsafe_allow_html=True,
            )


# ── Sidebar ───────────────────────────────────────────────────────────────
def render_sidebar():
    """Render the sidebar with chapter navigation, theme toggle, bookmarks, and export."""
    t = thm()

    # App title
    st.markdown(
        f'<div style="text-align: center; padding: 8px 0;">'
        f'<h2 style="margin: 0; font-size: 1.3rem; color: {t["primary"]};">\U0001f4da SST Tutor</h2>'
        f'<p style="margin: 2px 0 0 0; font-size: 0.8rem; color: {t["muted"]};">ICSE Class V</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Dark Mode Toggle ──
    dark_label = "\U0001f319 Switch to Light Mode" if st.session_state.dark_mode else "\U0001f31e Switch to Dark Mode"
    if st.button(dark_label, key="dark_mode_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")

    # Progress overview
    pct = get_progress_pct()
    st.markdown(f"**\U0001f4ca Progress: {pct:.0f}%**")
    st.progress(pct / 100)

    # Export button in sidebar
    if st.button("\U0001f4e5 Export Progress", key="sidebar_export_btn", use_container_width=True):
        st.session_state.show_export_panel = not st.session_state.get("show_export_panel", False)

    if st.session_state.get("show_export_panel", False):
        with st.container():
            render_export_buttons()

    st.markdown("---")

    # Home button
    if st.button("\U0001f3e0 Home", use_container_width=True, key="home_btn"):
        st.session_state.current_chapter = None
        st.session_state.current_section = None
        st.session_state.mode = "learn"
        st.session_state.quiz_questions = []
        st.rerun()

    st.markdown("---")

    # ── Bookmarks Section ──
    if st.session_state.bookmarks:
        with st.expander(f"\U0001f516 Bookmarks ({len(st.session_state.bookmarks)})", expanded=False):
            for bk in list(st.session_state.bookmarks):
                section, num = bk.rsplit("_", 1)
                num = int(num)
                ch = get_chapter(section, num)
                if ch:
                    col_b, col_r = st.columns([4, 1])
                    with col_b:
                        if st.button(f"{ch['emoji']} {ch['title']}", key=f"bk_side_{bk}", use_container_width=True):
                            st.session_state.current_section = section
                            st.session_state.current_chapter = num
                            st.session_state.mode = "learn"
                            st.session_state.quiz_questions = []
                            st.rerun()
                    with col_r:
                        if st.button("\u274c", key=f"bk_del_{bk}"):
                            st.session_state.bookmarks.remove(bk)
                            st.rerun()
        st.markdown("---")

    # Section colors
    section_colors = {
        "Geography": ("#82b1ff" if st.session_state.dark_mode else "#1565C0", "#e3f2fd"),
        "History": ("#ce93d8" if st.session_state.dark_mode else "#6a1b9a", "#f3e5f5"),
        "Civics": ("#ffab91" if st.session_state.dark_mode else "#e65100", "#fff3e0"),
    }

    # Chapter list
    for section in get_sections():
        color, bg = section_colors.get(section, ("#000", "#f5f5f5"))
        st.markdown(
            f'<div class="section-header" style="color: {color}; border-color: {color};">'
            f'{section}</div>',
            unsafe_allow_html=True,
        )

        for ch in CHAPTERS[section]:
            key = chapter_key(section, ch["num"])
            progress_info = st.session_state.progress.get(key, {})
            is_read = progress_info.get("read", False)
            is_active = (
                st.session_state.current_section == section
                and st.session_state.current_chapter == ch["num"]
            )

            status = "\u2705" if is_read else "\u2611\ufe0f"
            bookmark_icon = "\U0001f516 " if key in st.session_state.bookmarks else ""
            active_class = "active" if is_active else ""
            quiz_s = progress_info.get("quiz_score", 0)
            quiz_t = progress_info.get("quiz_total", 0)
            quiz_badge = f" ({quiz_s}/{quiz_t})" if quiz_t > 0 else ""

            st.markdown(
                f'<div class="chapter-card {active_class}">'
                f'{status} {bookmark_icon}<strong>Ch {ch["num"]}:</strong> {ch["emoji"]} {ch["title"]}{quiz_badge}'
                f'</div>',
                unsafe_allow_html=True,
            )

            label = f"{status} {bookmark_icon}Ch {ch['num']}: {ch['emoji']} {ch['title']}{quiz_badge}"
            if st.button(label, key=f"ch_{section}_{ch['num']}", use_container_width=True):
                st.session_state.current_section = section
                st.session_state.current_chapter = ch["num"]
                st.session_state.mode = "learn"
                st.session_state.quiz_questions = []
                st.rerun()

    st.markdown("---")
    st.caption("\U0001f50c Built with Wikipedia + Open Trivia DB + Web Resources")


# ── Main App ───────────────────────────────────────────────────────────────
render_sidebar()

if st.session_state.current_chapter is None:
    render_home()
else:
    chapter = get_chapter(st.session_state.current_section, st.session_state.current_chapter)
    if chapter is None:
        st.error("Chapter not found!")
        st.session_state.current_chapter = None
        st.rerun()
    else:
        mode_col1, mode_col2, mode_col3 = st.columns(3)

        with mode_col1:
            if st.button(
                "\U0001f4d6 Learn", key="mode_learn", use_container_width=True,
                type="primary" if st.session_state.mode == "learn" else "secondary",
            ):
                st.session_state.mode = "learn"
                st.session_state.quiz_questions = []
                st.rerun()

        with mode_col2:
            if st.button(
                "\U0001f9e0 Quiz", key="mode_quiz", use_container_width=True,
                type="primary" if st.session_state.mode == "quiz" else "secondary",
            ):
                st.session_state.mode = "quiz"
                st.rerun()

        with mode_col3:
            if st.button(
                "\U0001f50d Explore", key="mode_explore", use_container_width=True,
                type="primary" if st.session_state.mode == "explore" else "secondary",
            ):
                st.session_state.mode = "explore"
                st.rerun()

        st.markdown("---")

        if st.session_state.mode == "learn":
            render_learn_mode(chapter)
        elif st.session_state.mode == "quiz":
            render_quiz_mode(chapter)
        elif st.session_state.mode == "explore":
            render_explore_mode(chapter)