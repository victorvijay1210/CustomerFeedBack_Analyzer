from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.getenv("CUSTOMER_FEEDBACK_API_URL", "http://127.0.0.1:8000")


def clear_analysis() -> None:
    st.session_state.analysis_result = None


def fetch_feedback_history() -> list[dict[str, Any]]:
    try:
        response = requests.get(f"{API_BASE_URL}/feedback", timeout=10)
        if response.status_code != 200:
            st.error("Unable to load feedback history.")
            return []
        return response.json()
    except requests.RequestException:
        return []


def analyze_feedback(review: str) -> dict[str, Any] | None:
    if not review.strip():
        st.error("Please enter customer feedback.")
        return None

    try:
        with st.spinner("Analyzing sentiment..."):
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={"review": review},
                timeout=20,
            )

        if response.status_code == 200:
            result = response.json()
            st.session_state.analysis_result = result
            return result

        detail = response.json().get("detail", "Unable to analyze feedback. Please try again.")
        st.error(str(detail))
        return None
    except requests.RequestException:
        st.error("Backend service is unavailable. Please make sure FastAPI is running.")
        return None


def save_feedback(payload: dict[str, Any]) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback",
            json=payload,
            timeout=20,
        )
        if response.status_code == 200:
            st.success("Feedback saved successfully!")
            st.session_state.history = fetch_feedback_history()
            return True

        detail = response.json().get("detail", "Database error. Please try again.")
        st.error(str(detail))
        return False
    except requests.RequestException:
        st.error("Backend service is unavailable. Please make sure FastAPI is running.")
        return False


st.set_page_config(page_title="Customer Feedback Sentiment Analyzer", page_icon="💬")
st.title("Customer Feedback Sentiment Analyzer")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "history" not in st.session_state:
    st.session_state.history = []

review = st.text_area(
    "Enter customer feedback",
    height=180,
    placeholder="The product is great, but the delivery was very slow.",
)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Analyze Sentiment"):
        clear_analysis()
        analyze_feedback(review)

if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.markdown("---")
    st.subheader("Analysis Result")
    st.write(f"**Customer Feedback**\n{review}")
    st.write(f"**Sentiment**\n{result['sentiment']}")
    st.write(f"**Explanation**\n{result['explanation']}")

    if st.button("Save Response"):
        save_feedback(result)

st.markdown("---")
st.subheader("Feedback History")

if not st.session_state.history:
    st.session_state.history = fetch_feedback_history()

selected_sentiment = st.selectbox("Filter by sentiment", ["All", "Positive", "Negative", "Neutral"])

if st.session_state.history:
    filtered = st.session_state.history
    if selected_sentiment != "All":
        filtered = [entry for entry in st.session_state.history if entry.get("sentiment") == selected_sentiment]

    history_df = [
        {
            "Date": entry.get("created_at", ""),
            "Review": entry.get("review", ""),
            "Sentiment": entry.get("sentiment", ""),
            "Explanation": entry.get("explanation", ""),
        }
        for entry in filtered
    ]
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No saved feedback yet.")
