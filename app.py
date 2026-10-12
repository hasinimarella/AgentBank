"""AgentBank: simulated real-time banking assistant with a supervisor + specialised agents.

Run:  streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from agents.supervisor import Supervisor, SupervisorResponse
from config.settings import get_settings
from data.seed_data import seed_database
from database.db import connect, database_ready
from services.response_builder import format_inr

st.set_page_config(page_title="AgentBank · Multi-Agent Banking Simulator", page_icon="🏦", layout="wide")

EXAMPLES = [
    ("1 · Account balance", "What is the account balance for customer C1001?"),
    ("2 · Transaction history", "Show the last five transactions for customer C1002."),
    ("3 · Fraud-risk check", "Check transaction TXN-9003 for fraud risk."),
    ("4 · Loan eligibility", "Is customer C1001 eligible for a loan of ₹200000?"),
    ("5 · Financial summary", "Give me a complete financial summary for customer C1003."),
]
MORE_EXAMPLES = [
    ("Monthly spending", "Show the monthly spending analysis for customer C1002."),
    ("Missing customer ID", "Show my recent transactions."),
    ("Empty history", "Show the transactions for customer C1006."),
    ("Medium-risk txn", "Is TXN-9004 suspicious?"),
    ("Loan needs review", "Can customer C1002 borrow ₹6 lakh?"),
    ("Missing income data", "Is customer C1005 eligible for a loan of ₹200000?"),
    ("Needs clarification", "Is customer C1001 eligible for a loan?"),
    ("Unknown customer", "What is the balance for customer C9999?"),
    ("Unsupported action", "Transfer ₹5000 from C1001 to C1002."),
]
SCENARIOS = {
    "C1001": "Strong profile; loan ₹200000 eligible",
    "C1002": "9 transactions; loan ₹6 lakh needs review",
    "C1003": "Heavy debt; loan not eligible",
    "C1004": "Owns the suspicious transactions",
    "C1005": "Income not on file; dormant account",
    "C1006": "New customer; no transactions",
}
TXN_HINTS = {
    "TXN-9003": "HIGH (95): large foreign crypto debit at 02:10",
    "TXN-9004": "MEDIUM: new city, gift cards, late night",
    "TXN-9010": "HIGH: failed foreign attempt",
    "TXN-9102": "LOW: ordinary grocery spend (C1001)",
}

st.markdown(
    """
    <style>
      :root { --ab-blue: #2563eb; --ab-purple: #7c3aed; --ab-mint: #0f766e; }
      .stApp { background: linear-gradient(180deg, #f8fbff 0%, #ffffff 42%); }
      .block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1500px; }
      .ab-hero {padding: 1.35rem 1.55rem; border-radius: 20px;
                background: linear-gradient(115deg, #233b91 0%, #356fe8 56%, #7c3aed 100%);
                color: #fff; margin-bottom: .85rem; box-shadow: 0 10px 28px rgba(37, 99, 235, .18);}
      .ab-hero h1 {margin: 0; font-size: 2rem; color: #fff; letter-spacing: -.025em;}
      .ab-hero p {margin: .35rem 0 0 0; opacity: .96; font-size: 1rem;}
      .ab-welcome {padding: 1rem 1.1rem; border: 1px solid #dbeafe; border-radius: 16px;
                   background: linear-gradient(120deg, #eff6ff, #f5f3ff); margin: .8rem 0 1rem 0;}
      .ab-welcome h3 {margin: 0 0 .35rem 0; color: #1e3a8a;}
      div[data-testid="stChatMessage"] {border: 1px solid #e5eaf5; border-radius: 16px;
                   padding: .8rem 1rem; box-shadow: 0 3px 12px rgba(31, 41, 55, .035);}
      div[data-testid="stChatInput"] {border-color: #b8ccff; border-radius: 16px;}
      div[data-testid="stChatInput"]:focus-within {border-color: #4f46e5; box-shadow: 0 0 0 2px #c7d2fe;}
      section[data-testid="stSidebar"] {background: linear-gradient(180deg, #f0f5ff 0%, #faf5ff 100%);}
      section[data-testid="stSidebar"] button {border-radius: 11px; border-color: #d5def3;}
      section[data-testid="stSidebar"] button:hover {border-color: #818cf8; color: #3730a3;}
      .stAlert {border-radius: 13px;}
      @media (max-width: 640px) {
        .ab-hero h1 {font-size: 1.45rem;}
        .ab-hero {padding: 1rem;}
        .block-container {padding-top: .8rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- resources -------------------------------------------------------------------------------------
@st.cache_resource(show_spinner="Starting AgentBank…")
def get_supervisor() -> Supervisor:
    settings = get_settings()
    if not database_ready(settings.db_path):
        seed_database(settings.db_path)
    return Supervisor(settings=settings)


def reference_rows() -> pd.DataFrame:
    settings = get_settings()
    conn = connect(settings.db_path)
    try:
        rows = conn.execute("SELECT customer_id, full_name FROM customers ORDER BY customer_id").fetchall()
    finally:
        conn.close()
    return pd.DataFrame([{"ID": r["customer_id"], "Name": r["full_name"], "Scenario": SCENARIOS.get(r["customer_id"], "")} for r in rows])


def _df(rows: list[dict]) -> None:
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


supervisor = get_supervisor()

if "messages" not in st.session_state:
    st.session_state.messages = []


def queue_prompt(text: str) -> None:
    st.session_state.pending_prompt = text


def reset_conversation() -> None:
    st.session_state.messages = []


# ---- sidebar -------------------------------------------------------------------------------------------
mode = supervisor.mode
with st.sidebar:
    st.header("AI mode")
    if mode["mode"] == "LLM":
        st.success(f"🟢 **LLM mode** · {mode['provider']} · `{mode['model']}`")
    else:
        st.warning("🟡 **Fallback mode** · deterministic rules. No LLM is being called.")
    st.caption(mode["detail"])
    if st.button("Re-check LLM availability", width="stretch"):
        get_supervisor.clear()
        st.rerun()

    st.header("Try an example")
    for label, prompt_text in EXAMPLES:
        st.button(label, key=f"ex_{label}", on_click=queue_prompt, args=(prompt_text,), width="stretch", help=prompt_text)
    with st.expander("More scenarios"):
        for label, prompt_text in MORE_EXAMPLES:
            st.button(label, key=f"mx_{label}", on_click=queue_prompt, args=(prompt_text,), width="stretch", help=prompt_text)

    with st.expander("Customer & transaction IDs"):
        st.dataframe(reference_rows(), hide_index=True, width="stretch")
        st.markdown("\n".join(f"- `{k}` {v}" for k, v in TXN_HINTS.items()))

    st.button("🗑️ Reset conversation", on_click=reset_conversation, width="stretch")

# ---- header ------------------------------------------------------------------------------------------------
st.markdown(
    '<div class="ab-hero"><h1>🏦 AgentBank</h1>'
    "<p>Your friendly banking assistant. What can I help you with today?</p></div>",
    unsafe_allow_html=True,
)
st.caption("🔒 Demo only · All banking data is synthetic. Fraud and loan results are illustrative.")


# ---- rendering helpers --------------------------------------------------------------------------------------------
def render_result_panel(resp: dict) -> None:
    rtype, data = resp.get("result_type"), resp.get("result_data") or {}
    if not data or resp["status"] not in ("ok", "partial"):
        return
    if rtype == "balance":
        b = data["balance"]
        st.metric("Total balance", format_inr(b["total_balance"]))
        _df([{"Account": a["account_id"], "Type": a["account_type"], "Balance": format_inr(a["balance"]),
              "Status": a["status"]} for a in b["accounts"]])
    elif rtype == "transactions":
        h = data["history"]
        if h["returned"] == 0:
            st.info("No transactions found.")
        else:
            _df([{"ID": t["transaction_id"], "When": t["occurred_at"].replace("T", " "),
                  "Amount": ("+" if t["direction"] == "CREDIT" else "-") + format_inr(t["amount"]),
                  "Merchant": t["merchant"], "Where": f"{t['city']}, {t['country']}", "Status": t["status"]}
                 for t in h["transactions"]])
    elif rtype == "transaction":
        t = data["transaction"]
        _df([{k.replace("_", " ").title(): v for k, v in t.items()}])
    elif rtype == "fraud":
        a = data["assessment"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk score", f"{a['risk_score']} / 100")
        c2.metric("Risk level", a["risk_level"])
        c3.metric("Recommended action", a["recommended_action"])
        st.progress(a["risk_score"] / 100)
        level = a["risk_level"]
        (st.error if level == "HIGH" else st.warning if level == "MEDIUM" else st.success)(
            f"{level} risk · recommended action: {a['recommended_action']} · suspicious ≠ confirmed fraud")
        _df([{"Indicator": i["indicator"].replace("_", " "), "Triggered": "yes" if i["triggered"] else "no",
              "Points": f"{i['points']}/{i['max_points']}", "Reason": i["reason"]} for i in a["all_indicators"]])
        st.markdown("**Recommended next steps**")
        for r in a["recommendations"]:
            st.markdown(f"- {r}")
        st.caption(f"{a['engine']['name']} · {a['engine']['kind']}")
    elif rtype == "loan":
        a = data["assessment"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Requested", format_inr(a["requested_amount"], 0))
        c2.metric("Decision (illustrative)", a["decision"].replace("_", " ").title())
        if a["dti_after_loan"] is not None:
            c3.metric("Debt-to-income after loan", f"{a['dti_after_loan']:.1%}")
        if a["checks"]:
            _df([{"Check": c["check"].replace("_", " "), "Outcome": c["outcome"], "Detail": c["detail"]} for c in a["checks"]])
        if a["missing_information"]:
            st.warning("Missing: " + ", ".join(a["missing_information"]))
        st.caption(f"{a['engine']['name']} · {a['engine']['kind']}")
    elif rtype == "spending":
        s = data["spending"]
        if not s["transaction_count"]:
            st.info("No completed spending found for the selected month.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Spent in {s['month']}", format_inr(s["total_spent"]))
            c2.metric("Completed debits", s["transaction_count"])
            c3.metric("Average per debit", format_inr(s["average_per_transaction"]))
            chart = pd.DataFrame({"Category": [c["category"].replace("_", " ").title() for c in s["by_category"]],
                                  "Amount (INR)": [c["amount"] for c in s["by_category"]]}).set_index("Category")
            st.bar_chart(chart, horizontal=True)
            _df([{"Merchant": m["merchant"], "Amount": format_inr(m["amount"])} for m in s["top_merchants"]])
    elif rtype == "summary":
        s = data["summary"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total balance", format_inr(s.get("total_balance")) if "total_balance" in s else "n/a")
        cp = s.get("credit_profile") or {}
        c2.metric("Credit score", cp.get("credit_score") if cp.get("credit_score") is not None else "n/a")
        c3.metric("Debt-to-income", f"{cp['current_dti']:.1%}" if cp.get("current_dti") is not None else "n/a")
        if s.get("accounts"):
            _df([{"Account": a["account_id"], "Type": a["account_type"], "Balance": format_inr(a["balance"]),
                  "Status": a["status"]} for a in s["accounts"]])
        if s.get("recent_transactions"):
            st.markdown("**Recent transactions**")
            _df([{"ID": t["transaction_id"], "When": t["occurred_at"].replace("T", " "),
                  "Amount": ("+" if t["direction"] == "CREDIT" else "-") + format_inr(t["amount"]),
                  "Merchant": t["merchant"], "Category": t["category"].replace("_", " ").title(), "Status": t["status"]}
                 for t in s["recent_transactions"]])
        act = s.get("activity")
        if act and act["top_spending_categories"]:
            st.markdown("**Top spending categories**")
            st.bar_chart(pd.DataFrame({"Category": [c["category"].replace("_", " ").title() for c in act["top_spending_categories"]],
                                       "Amount (INR)": [c["amount"] for c in act["top_spending_categories"]]}).set_index("Category"),
                         horizontal=True)


def render_trace(trace: dict) -> None:
    with st.expander(f"🔎 Execution trace · {trace['trace_id']}", expanded=False):
        c = st.columns(5)
        c[0].metric("Intent", trace["intent"] or "—")
        c[1].metric("Classified by", {"llm": "LLM", "fallback": "Rules"}.get(trace["intent_source"] or "", "—"))
        c[2].metric("Agent", trace["selected_agent"] or "—")
        c[3].metric("Status", trace["response_status"])
        c[4].metric("Time", f"{trace['duration_ms']:.0f} ms")
        st.caption(f"Extracted entities: `{trace['entities']}`")
        llm = trace.get("llm") or {}
        if llm.get("used"):
            st.caption(f"LLM call: {llm.get('provider')}/{llm.get('model')} (output validated before use)")
        elif llm.get("error"):
            st.caption(f"LLM call failed ({llm['error']}); deterministic fallback was used.")
        else:
            st.caption("No LLM was called for this request (fallback mode).")
        t_steps, t_tools, t_raw = st.tabs(["Steps", "Tool calls", "Raw trace JSON"])
        with t_steps:
            _df([{"#": s["n"], "Actor": s["actor"], "Action": s["action"], "Detail": str(s["detail"]), "t (ms)": s["t_ms"]}
                 for s in trace["steps"]])
        with t_tools:
            if trace["tool_calls"]:
                _df([{"Agent": t["agent"], "Tool": t["tool"], "Status": t["status"], "ms": t["duration_ms"],
                      "Error": t["error_code"] or "", "Args": str(t["args"])} for t in trace["tool_calls"]])
                st.caption("Results below are sanitised (contact details redacted, long lists truncated).")
                st.json([{"tool": t["tool"], "result": t["result"]} for t in trace["tool_calls"]], expanded=False)
            else:
                st.info("No tools were called.")
        with t_raw:
            st.json(trace, expanded=False)


def render_assistant(entry: dict) -> None:
    resp = entry["response"]
    status = resp["status"]
    if status == "clarification":
        st.info(entry["content"], icon="❓")
    elif status in ("not_found", "invalid_input"):
        st.warning(entry["content"], icon="🔍")
    elif status == "error":
        st.error(entry["content"])
    elif status in ("unsupported", "empty"):
        st.info(entry["content"], icon="ℹ️")
    else:
        st.markdown(entry["content"])
    for n in resp.get("notices", []):
        st.caption(f"⚠️ {n}")
    if resp.get("ai_summary"):
        st.info(f"**AI-phrased summary** ({resp['mode']['provider']}; every number was checked against tool results):\n\n{resp['ai_summary']}")
    render_result_panel(resp)
    render_trace(resp["trace"])


# ---- handle input ------------------------------------------------------------------------------------------------------
typed = st.chat_input("Ask about a balance, transactions, fraud risk, a loan or a summary…")
prompt = typed or st.session_state.pop("pending_prompt", None)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        response: SupervisorResponse = supervisor.handle(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.message, "response": response.to_dict()})
    except Exception:  # last-resort boundary: the UI must stay usable
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Something unexpected went wrong. No data was changed. Please try again.",
            "response": {"status": "error", "notices": [], "trace": {
                "trace_id": "n/a", "intent": None, "intent_source": None, "selected_agent": None,
                "response_status": "error", "duration_ms": 0, "entities": {}, "steps": [], "tool_calls": [], "llm": {}}},
        })

# ---- main chat page ----------------------------------------------------------------
if not st.session_state.messages:
    st.markdown("### 👋 Welcome!")
    st.markdown("Choose a quick prompt or type your question below.")
    quick_examples = [
        ("💰 Account balance", "What is the account balance for customer C1001?"),
        ("💳 Transactions", "Show the last five transactions for customer C1002."),
        ("🛡️ Fraud check", "Check transaction TXN-9003 for fraud risk."),
        ("🏦 Loan eligibility", "Is customer C1001 eligible for a loan of ₹200000?"),
    ]
    cols = st.columns(2)
    for i, (label, prompt_text) in enumerate(quick_examples):
        with cols[i % 2]:
            st.button(
                label,
                key=f"quick_{i}",
                on_click=queue_prompt,
                args=(prompt_text,),
                width="stretch",
            )

for entry in st.session_state.messages:
    with st.chat_message(entry["role"], avatar="🧑" if entry["role"] == "user" else "🏦"):
        if entry["role"] == "user":
            st.markdown(entry["content"])
        else:
            render_assistant(entry)

st.caption("🔒 Demo environment · All customer, account and transaction data is synthetic. AgentBank is not production banking software.")