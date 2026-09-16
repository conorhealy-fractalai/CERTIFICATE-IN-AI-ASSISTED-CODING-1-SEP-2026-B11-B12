"""Streamlit front end for ExpenseFlow: submit, list, and get AI insights on expenses."""

import os

import httpx
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

STATUS_LABELS = {
    "pending": "🟡 Pending",
    "approved": "🟢 Approved",
    "rejected": "🔴 Rejected",
}


def format_minor(amount_minor: int) -> str:
    """Format integer minor units as a currency string with two decimals, for display only."""
    return f"{amount_minor / 100:,.2f}"


st.set_page_config(page_title="ExpenseFlow", page_icon="💸")
st.title("💸 ExpenseFlow")
st.caption("Submit, review, and get AI-generated insights on expenses.")

st.header("Submit a new expense")
with st.form("submit_expense", clear_on_submit=True):
    description = st.text_input("Description")
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
    with col2:
        currency = st.text_input("Currency", value="INR", max_chars=3)
    category = st.text_input("Category")
    submitted_by = st.text_input("Submitted by")
    submit_clicked = st.form_submit_button("Submit expense", disabled=st.session_state.get("submitting", False))

    if submit_clicked:
        st.session_state["submitting"] = True
        try:
            response = httpx.post(
                f"{API_BASE}/expenses",
                json={
                    "description": description,
                    "amount_minor": int(round(amount * 100)),
                    "currency": currency.upper(),
                    "category": category,
                    "submitted_by": submitted_by,
                },
                timeout=10,
            )
            response.raise_for_status()
            st.success("Expense submitted.")
        except httpx.RequestError:
            st.error(f"Could not reach the ExpenseFlow API at {API_BASE}. Is it running?")
        except httpx.HTTPStatusError as exc:
            st.error(f"API rejected the request: {exc.response.text}")
        finally:
            st.session_state["submitting"] = False

st.header("Expenses")
try:
    response = httpx.get(f"{API_BASE}/expenses", timeout=10)
    response.raise_for_status()
    expenses = response.json()
    if not expenses:
        st.info("No expenses yet. Submit one above.")
    else:
        rows = [
            {
                "ID": e["id"],
                "Description": e["description"],
                "Category": e["category"],
                "Amount": format_minor(e["amount_minor"]),
                "Currency": e["currency"],
                "Status": STATUS_LABELS.get(e["status"], e["status"]),
                "Submitted by": e["submitted_by"],
            }
            for e in expenses
        ]
        st.table(rows)
except httpx.RequestError:
    st.error(f"Could not reach the ExpenseFlow API at {API_BASE}. Is it running?")

st.header("AI insights")
if st.button("Generate insights"):
    try:
        response = httpx.get(f"{API_BASE}/reports/insights", timeout=30)
        response.raise_for_status()
        data = response.json()
        st.subheader(data.get("summary", ""))
        for bullet in data.get("bullets", []):
            st.markdown(f"- {bullet}")
    except httpx.RequestError:
        st.error(f"Could not reach the ExpenseFlow API at {API_BASE}. Is it running?")
