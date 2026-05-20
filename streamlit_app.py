"""
Customer Support Chatbot — Streamlit Demo App

Run with:
    streamlit run streamlit_app.py

This app demonstrates the LangGraph customer-support workflow with
5 preset test cases plus free-form chat input.
"""

import os
import sys

# Ensure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
from workflow import process_message
from config import SAMPLE_MESSAGES

st.set_page_config(
    page_title="Customer Support AI",
    page_icon="🎧",
    layout="centered",
)

# ──────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎧 Customer Support AI")
    st.markdown(
        """
        This demo showcases a **LangGraph** workflow that:

        1. **Classifies** customer intent
        2. **Detects** sentiment & assigns priority
        3. **Decides** if human escalation is needed
        4. **Generates** an empathetic response

        ---
        **Architecture**
        ```
        START → classify → escalation_check
                        ├─[False]→ auto_respond → END
                        └─[True] → human_handoff → END
        ```
        """
    )
    st.divider()
    st.caption("Powered by OpenRouter LLM + LangGraph")


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def color_for_sentiment(sentiment: str) -> str:
    return {
        "angry": "red",
        "negative": "orange",
        "neutral": "gray",
        "positive": "green",
    }.get(sentiment, "gray")


def color_for_priority(priority: str) -> str:
    return {
        "urgent": "red",
        "high": "orange",
        "medium": "blue",
        "low": "green",
    }.get(priority, "gray")


def run_workflow(message: str):
    """Invoke the graph and return the result dict."""
    with st.spinner("🤖 Analyzing message…"):
        result = process_message(message)
    return result


def display_result(result: dict):
    """Render the workflow result in a polished card layout."""
    st.divider()

    cols = st.columns(4)
    with cols[0]:
        st.metric("Intent", result["intent"].replace("_", " ").title())
    with cols[1]:
        st.metric(
            "Sentiment",
            result["sentiment"].title(),
        )
    with cols[2]:
        st.metric("Priority", result["priority"].upper())
    with cols[3]:
        st.metric("Escalate", "🚨 Yes" if result["escalate"] else "✅ No")

    # Reasoning
    with st.expander("📋 Routing Reasoning", expanded=True):
        st.write(result["reasoning"])

    # Response
    st.subheader("💬 Generated Response")
    if result["escalate"]:
        st.error(result["response"])
    else:
        st.success(result["response"])


# ──────────────────────────────────────────────────────────────
# Main UI
# ──────────────────────────────────────────────────────────────
st.title("Customer Support Chatbot Demo")
st.markdown("Choose a preset test case or type your own message below.")

# 5 representative test cases from SAMPLE_MESSAGES
TEST_CASES = [
    ("📦 Shipping Inquiry", SAMPLE_MESSAGES[0]["message"]),
    ("💰 Refund Request", SAMPLE_MESSAGES[1]["message"]),
    ("😡 Angry Complaint (Escalation)", SAMPLE_MESSAGES[2]["message"]),
    ("❓ Product Question", SAMPLE_MESSAGES[3]["message"]),
    ("⚠️ Scam Report (Escalation)", SAMPLE_MESSAGES[6]["message"]),
]

st.subheader("Preset Test Cases")
preset_cols = st.columns(5)
for idx, (label, msg) in enumerate(TEST_CASES):
    with preset_cols[idx]:
        if st.button(label, use_container_width=True):
            st.session_state["last_message"] = msg
            st.session_state["result"] = run_workflow(msg)

st.divider()

# Free-form input
st.subheader("Or type a custom message")
with st.form("chat_form", clear_on_submit=False):
    user_input = st.text_area(
        "Customer message",
        placeholder="e.g. I want a refund for my broken headphones…",
        height=100,
    )
    submitted = st.form_submit_button("🚀 Process Message")

if submitted and user_input.strip():
    st.session_state["last_message"] = user_input.strip()
    st.session_state["result"] = run_workflow(user_input.strip())

# Display result if available
if "result" in st.session_state:
    st.info(f"**Input:** {st.session_state['last_message']}")
    display_result(st.session_state["result"])
