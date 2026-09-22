import re
import streamlit as st
from api_client import ask_question

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded"
)

ACCENT = "#E8590C"   # used ONLY for: title, hover state, assistant avatar — nowhere else
INK = "#FBF7F2"
MUTED = "#9C9086"
MUTED_DIM = "#6E645A"
BG = "#141110"
CARD = "#1C1815"
BORDER = "#332A21"

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    /* Kill the stray decoration bar Streamlit renders at the very top */
    div[data-testid="stDecoration"] {{ display: none !important; }}
    div[data-testid="stStatusWidget"] {{ display: none !important; }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
    }}
    header[data-testid="stHeader"]::before,
    header[data-testid="stHeader"]::after {{
        display: none !important;
    }}
    /* Streamlit sometimes paints a rainbow progress/decoration strip at the
       very top edge of the app on load/rerun — force it off everywhere. */
    div[data-testid="stAppViewContainer"] > div:first-child {{
        background: {BG} !important;
    }}
    body, html {{ background: {BG} !important; }}

    .stApp {{ background: {BG}; }}
    div[data-testid="stMainBlockContainer"],
    div.block-container {{
        padding-top: 2.5rem !important;
    }}

    /* ---- Hero ---- */
    .hero-wrap {{ text-align: center; padding-bottom: 8px; margin-top: 9vh; }}
    .hero-mark {{
        width: 52px; height: 52px; border-radius: 14px;
        background: {ACCENT}; color: #FFF;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 800;
        margin: 0 auto 18px auto;
    }}
    .hero-title {{
        font-size: 46px;
        font-weight: 800;
        color: {INK};
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }}
    .hero-title span {{ color: {ACCENT}; }}
    .hero-subtitle {{
        color: {MUTED};
        font-size: 15.5px;
        margin-top: 0px;
        margin-bottom: 30px;
    }}
    .try-label {{
        color: {INK};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 12px;
    }}
    .stat-badge {{
        display: inline-block;
        background: {CARD};
        color: {MUTED};
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12.5px;
        font-weight: 600;
        border: 1px solid {BORDER};
        margin-bottom: 18px;
    }}
    .stat-badge b {{ color: {ACCENT}; }}

    /* ---- Suggestion buttons: tinted, clearly clickable ---- */
    div[data-testid="stButton"] > button {{
        background: #1F1712 !important;
        color: {INK} !important;
        border: 1px solid #4A3420 !important;
        border-radius: 10px !important;
        padding: 16px 18px !important;
        text-align: left !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        height: 100% !important;
        transition: 0.15s;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: #2A1D13 !important;
        border-color: {ACCENT} !important;
        color: {INK} !important;
        transform: translateY(-1px);
    }}

    /* ---- Chat bubbles ---- */
    [data-testid="stChatMessage"] {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 6px 8px;
        margin-bottom: 12px;
    }}
    [data-testid="stChatMessageAvatarUser"] {{ background: {MUTED_DIM} !important; }}
    [data-testid="stChatMessageAvatarAssistant"] {{ background: {ACCENT} !important; }}

    .source-box {{
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid {BORDER};
    }}
    .source-label {{
        display: flex;
        align-items: center;
        gap: 7px;
        color: {INK};
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 10px;
    }}
    .source-item {{
        display: flex;
        align-items: center;
        background: #1F1712;
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 13px;
        color: {INK};
    }}
    .source-item .file-icon {{
        margin-right: 10px;
        flex-shrink: 0;
        font-size: 14px;
        opacity: 0.85;
    }}

    /* ---- Error message styling (backend unreachable, etc.) ---- */
    .error-box {{
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: #2A1512;
        border: 1px solid #5C2A22;
        border-radius: 10px;
        padding: 12px 14px;
        color: #F2B8AD;
        font-size: 13.5px;
        line-height: 1.55;
    }}
    .error-box .err-icon {{ flex-shrink: 0; font-size: 15px; }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background-color: #17130F;
        border-right: 1px solid {BORDER};
    }}
    .side-brand {{
        display: flex; align-items: center; gap: 9px;
        font-size: 17px; font-weight: 800; color: {INK};
        margin: 4px 0 20px 0;
    }}
    .side-brand .mark {{
        width: 26px; height: 26px; border-radius: 7px;
        background: {ACCENT}; color: #FFF;
        display: flex; align-items: center; justify-content: center;
        font-size: 13px; font-weight: 800; flex-shrink: 0;
    }}
    .side-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }}
    .side-label {{
        color: {MUTED_DIM};
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }}
    .side-body {{ color: {MUTED}; font-size: 13px; line-height: 1.55; }}
    .domain-row {{ display: flex; align-items: center; margin: 7px 0; font-size: 13.5px; color: {INK}; }}
    .domain-dot {{ width: 5px; height: 5px; border-radius: 50%; display: inline-block; margin-right: 11px; background: {MUTED_DIM}; }}
    .sys-row {{
        font-size: 12.5px;
        line-height: 1.9;
        color: {MUTED};
    }}
    .sys-row b {{ color: {INK}; font-weight: 600; }}

    /* ---- Chat input: blends with the page, no separate footer band ---- */
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"],
    [data-testid="stChatInput"],
    .stChatFloatingInputContainer,
    div:has(> [data-testid="stChatInput"]) {{
        background: {BG} !important;
    }}
    [data-testid="stBottom"] * {{
        background-color: transparent;
    }}
    [data-testid="stBottomBlockContainer"] {{
        padding-top: 18px !important;
        padding-bottom: 22px !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        color: {INK} !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
    }}
    [data-testid="stChatInput"]:focus-within textarea {{
        border-color: #4A3420 !important;
    }}
    [data-testid="stBottom"] {{
        border-top: none !important;
    }}

    /* ---- Send button: clear, tappable, accent-colored ---- */
    [data-testid="stChatInputSubmitButton"] {{
        background: {ACCENT} !important;
        border-radius: 10px !important;
        border: none !important;
        opacity: 1 !important;
    }}
    [data-testid="stChatInputSubmitButton"] svg {{
        fill: #FFFFFF !important;
    }}
    [data-testid="stChatInputSubmitButton"]:hover {{
        background: #C94A0A !important;
    }}
    [data-testid="stChatInputSubmitButton"]:disabled {{
        background: {BORDER} !important;
        opacity: 1 !important;
    }}
    [data-testid="stChatInputSubmitButton"]:disabled svg {{
        fill: {MUTED_DIM} !important;
    }}

    /* ---- Destructive button (Clear conversation) ---- */
    div[data-testid="stButton"] > button[kind="secondary"].clear-btn,
    .clear-btn-wrap div[data-testid="stButton"] > button {{
        background: #1F1712 !important;
        color: #E8827A !important;
        border: 1px solid #4A2620 !important;
        text-align: center !important;
    }}
    .clear-btn-wrap div[data-testid="stButton"] > button:hover {{
        background: #2A1512 !important;
        border-color: #C94A0A !important;
        color: #F2B8AD !important;
    }}
    .clear-confirm-card {{
        background: {CARD};
        border: 1px solid #4A2620;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }}
    .clear-confirm-card .cc-title {{
        color: {INK};
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 4px;
    }}
    .clear-confirm-card .cc-body {{
        color: {MUTED};
        font-size: 12.5px;
        line-height: 1.5;
    }}
    .clear-confirm-wrap {{ margin-top: 10px; }}
    .clear-confirm-wrap div[data-testid="stButton"] > button {{
        font-size: 12.5px !important;
        padding: 9px 12px !important;
        background: {CARD} !important;
        color: {INK} !important;
        border: 1px solid {BORDER} !important;
    }}
    .clear-confirm-wrap div[data-testid="stButton"] > button:hover {{
        border-color: {MUTED_DIM} !important;
    }}
    .clear-confirm-wrap div[data-testid="column"]:last-child div[data-testid="stButton"] > button,
    .clear-confirm-wrap div[data-testid="stColumn"]:last-child div[data-testid="stButton"] > button {{
        background: #4A1712 !important;
        color: #FFD9D2 !important;
        border: 1px solid #7A2A1D !important;
        font-weight: 600 !important;
    }}
    .clear-confirm-wrap div[data-testid="column"]:last-child div[data-testid="stButton"] > button:hover,
    .clear-confirm-wrap div[data-testid="stColumn"]:last-child div[data-testid="stButton"] > button:hover {{
        background: #6B2018 !important;
        border-color: #C94A0A !important;
    }}

    /* ---- Stack suggestion / quick-ask columns on narrow screens ---- */
    @media (max-width: 640px) {{
        div[data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
        }}
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
        }}
        .hero-title {{ font-size: 34px !important; }}
    }}
    </style>
""", unsafe_allow_html=True)


def strip_inline_sources(answer: str) -> str:
    """
    The LLM sometimes appends its own 'Source:' / 'Sources:' section
    (plus bullet points) at the end of the answer text. We already
    render a dedicated, styled Sources box from entry["sources"], so
    that inline section is redundant and gets stripped here before
    the answer is displayed.
    """
    if not answer:
        return answer

    # Cut everything from a line that is just "Source:" / "Sources:"
    # (optionally bold/markdown-wrapped) to the end of the text.
    pattern = re.compile(
        r"\n{1,2}\s*(?:\*\*)?Sources?:?(?:\*\*)?\s*\n(?:.*\n?)*$",
        re.IGNORECASE,
    )
    cleaned = pattern.sub("", answer)
    return cleaned.rstrip()


# ---- Sidebar ----
with st.sidebar:
    st.markdown('<div class="side-brand"><span class="mark">AI</span> Study Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-card"><div class="side-label">ABOUT</div>'
        f'<div class="side-body">A <b style="color:{INK}">Retrieval-Augmented Generation</b> system. '
        'It answers strictly from real university textbooks — never from the model\'s own memory.</div></div>',
        unsafe_allow_html=True,
    )
    domains = ["Machine Learning", "Deep Learning", "NLP", "Computer Vision"]
    domain_rows = "".join([f'<div class="domain-row"><span class="domain-dot"></span>{n}</div>' for n in domains])
    st.markdown(f'<div class="side-card"><div class="side-label">KNOWLEDGE DOMAINS</div>{domain_rows}</div>', unsafe_allow_html=True)

    sys_rows = "".join([
        f'<div class="sys-row">{k}: <b>{v}</b></div>'
        for k, v in [("Embedding", "all-MiniLM-L6-v2"), ("Vector DB", "ChromaDB"), ("LLM", "llama3.2:1b")]
    ])
    st.markdown(f'<div class="side-card"><div class="side-label">SYSTEM</div>{sys_rows}</div>', unsafe_allow_html=True)

    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False

    if not st.session_state.confirm_clear:
        st.markdown('<div class="clear-btn-wrap">', unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.confirm_clear = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="clear-confirm-card">'
            '<div class="cc-title">Delete this conversation?</div>'
            '<div class="cc-body">This can\'t be undone — all questions and answers will be removed.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="clear-confirm-wrap">', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        if cc1.button("Cancel", use_container_width=True):
            st.session_state.confirm_clear = False
            st.rerun()
        if cc2.button("Delete", use_container_width=True):
            st.session_state.history = []
            st.session_state.confirm_clear = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---- Session state ----
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

is_empty = len(st.session_state.history) == 0

suggestions = [
    "What is a convolutional neural network?",
    "What is stemming in NLP?",
    "What is overfitting in machine learning?",
    "What is image segmentation?",
]

# ---- Hero (only shown when conversation is empty) ----
if is_empty:
    st.markdown(
        '<div class="hero-wrap">'
        '<div class="hero-title"><span>AI</span> Study Assistant</div>'
        '<div class="hero-subtitle">Grounded answers from real ML, DL, NLP &amp; CV textbooks — powered by RAG.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="try-label">Try asking</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cols = [c1, c2, c1, c2]
    for i, sug in enumerate(suggestions):
        if cols[i].button(f"→  {sug}", key=f"sug_{i}", use_container_width=True):
            st.session_state.pending_question = sug
else:
    st.markdown(f'<span class="stat-badge"><b>{len(st.session_state.history)}</b> questions asked</span>', unsafe_allow_html=True)
    # compact, persistent quick-ask row once a conversation is underway
    qcols = st.columns(4)
    for i, sug in enumerate(suggestions):
        short = sug if len(sug) <= 26 else sug[:24] + "…"
        if qcols[i].button(short, key=f"sug_compact_{i}", use_container_width=True):
            st.session_state.pending_question = sug

# ---- Render existing conversation (oldest → newest, normal chat order) ----
for entry in st.session_state.history:
    with st.chat_message("user", avatar="🙂"):
        st.write(entry["question"])
    with st.chat_message("assistant", avatar="🤖"):
        if entry.get("is_error"):
            st.markdown(
                f'<div class="error-box"><span class="err-icon">⚠️</span><span>{entry["answer"].replace(chr(10), "<br>")}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.write(strip_inline_sources(entry["answer"]))
            if entry["sources"]:
                items = "".join([f'<div class="source-item"><span class="file-icon">📄</span>{s}</div>' for s in entry["sources"]])
                st.markdown(f'<div class="source-box"><div class="source-label">📚 Sources</div>{items}</div>', unsafe_allow_html=True)


def handle_question(q):
    with st.spinner("Searching textbooks…"):
        try:
            result = ask_question(q)
            st.session_state.history.append({
                "question": q, "answer": result["answer"], "sources": result["sources"], "is_error": False
            })
        except Exception as e:
            st.session_state.history.append({
                "question": q,
                "answer": f"Could not reach the backend. Make sure the API server is running.\n\nDetails: {e}",
                "sources": [],
                "is_error": True,
            })


# ---- Handle a suggestion-chip click ----
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    handle_question(q)
    st.rerun()

# ---- Chat input pinned at the bottom ----
typed_question = st.chat_input("Ask about ML, DL, NLP, or Computer Vision…")
if typed_question:
    handle_question(typed_question)
    st.rerun()