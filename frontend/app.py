import streamlit as st
from api_client import ask_question

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at top left, #1a2138 0%, #0b0f19 60%);
    }

    .hero-title {
        font-size: 44px;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        animation: shimmer 4s ease-in-out infinite;
        background-size: 200% auto;
    }

    @keyframes shimmer {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 16px;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    div[data-testid="stForm"] {
        background-color: #161d2e;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #2a3550;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.1);
    }

    .stTextInput > div > div > input {
        background-color: #0e1420;
        color: #f1f5f9;
        border-radius: 10px;
        border: 1px solid #2a3550;
        padding: 12px;
        font-size: 15px;
    }

    .stFormSubmitButton > button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed, #db2777);
        background-size: 200% auto;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 0px;
        font-weight: 600;
        font-size: 15px;
        transition: 0.4s;
    }
    .stFormSubmitButton > button:hover {
        background-position: right center;
        transform: scale(1.01);
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .chat-question {
        background: linear-gradient(135deg, #1e293b, #253349);
        color: #e2e8f0;
        padding: 14px 18px;
        border-radius: 14px 14px 4px 14px;
        margin: 10px 0 6px auto;
        max-width: 85%;
        font-weight: 500;
        text-align: right;
        margin-left: auto;
        animation: fadeIn 0.4s ease-out;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    .chat-answer {
        background-color: #101a2c;
        border: 1px solid #2a3550;
        border-left: 3px solid #7c3aed;
        color: #f1f5f9;
        padding: 16px 20px;
        border-radius: 14px 14px 14px 4px;
        margin: 6px auto 6px 0;
        max-width: 90%;
        line-height: 1.6;
        animation: fadeIn 0.5s ease-out;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    .source-tag {
        display: inline-block;
        background-color: #1e2a44;
        color: #7dd3fc;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        margin: 4px 4px 0 0;
        border: 1px solid #2a3550;
        transition: 0.2s;
    }
    .source-tag:hover {
        background-color: #26375c;
        transform: translateY(-1px);
    }

    .stat-badge {
        display: inline-block;
        background: linear-gradient(90deg, #1e2a44, #253349);
        color: #a78bfa;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #2a3550;
        margin-bottom: 16px;
    }

    section[data-testid="stSidebar"] {
        background-color: #0e1420;
        border-right: 1px solid #2a3550;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero-title"><span style="-webkit-text-fill-color: initial;">📚</span> AI Study Assistant</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="hero-subtitle">Grounded answers from real ML, DL, NLP & CV textbooks — powered by RAG.</div>',
    unsafe_allow_html=True
)

if "history" not in st.session_state:
    st.session_state.history = []

if len(st.session_state.history) > 0:
    st.markdown(f'<span class="stat-badge">💬 {len(st.session_state.history)} questions asked</span>', unsafe_allow_html=True)

with st.form(key="question_form", clear_on_submit=True):
    question = st.text_input(
        "Ask your question",
        placeholder="e.g. What is a convolutional neural network?",
        label_visibility="collapsed"
    )
    submitted = st.form_submit_button("✨ Ask", use_container_width=True)

if submitted and question.strip():
    with st.spinner("🔎 Searching textbooks and generating a grounded answer..."):
        try:
            result = ask_question(question)
            st.session_state.history.append({
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"]
            })
        except Exception as e:
            st.error(f"⚠️ Could not reach the backend. Make sure the API server is running.\n\nDetails: {e}")

if st.session_state.history:
    st.write("")
    for entry in reversed(st.session_state.history):
        st.markdown(f'<div class="chat-question">🧑 {entry["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-answer">🤖 {entry["answer"]}</div>', unsafe_allow_html=True)
        sources_html = "".join([f'<span class="source-tag">📄 {s}</span>' for s in entry["sources"]])
        st.markdown(sources_html, unsafe_allow_html=True)
        st.write("")
else:
    st.info("👋 Ask a question above to get started — try one about ML, DL, NLP, or Computer Vision.")

with st.sidebar:
    st.markdown("### ℹ️ About this assistant")
    st.write(
        "This is a **Retrieval-Augmented Generation (RAG)** system. "
        "It answers strictly from the content of real university textbooks — "
        "not from the model's own memory."
    )
    st.markdown("### 📂 Knowledge domains")
    st.markdown("- 🤖 Machine Learning\n- 🧠 Deep Learning\n- 💬 NLP\n- 👁️ Computer Vision")
    st.markdown("---")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()