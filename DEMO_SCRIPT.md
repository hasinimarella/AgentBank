# Demo Script (about 8-9 minutes)

All IDs and prompts below exist in the seeded data. Lines starting with **Type:** are the exact prompts to enter.
Nothing here claims a video has been recorded. This is a plan for recording one.

**Before you start:** run `start.bat` (or `python -m streamlit run app.py`), open http://localhost:8501, click **Reset conversation**.
Check the sidebar: expect the yellow **Fallback mode** badge (no LLM). If Ollama is installed and the model is pulled it shows **LLM mode**; both are fine.

---

## 0:00 - 0:45 Introduction
Say: "AgentBank is a simulated banking assistant. A **Supervisor agent** understands a question, validates it and routes it to a **Banking**, **Fraud** or **Loan** agent.
Those agents call simulated banking tools over synthetic data. All data is fake and nothing connects to a real bank. It needs no API key and runs offline."
Point at the yellow banner: "All data is simulated."

## 0:45 - 2:00 Architecture
Open the **Architecture & workflow** tab. Walk the diagram: UI → Supervisor → classifier (rules by default, optional local LLM) → router → agent → allow-listed tools → SQLite.
Open **Agents & tools**: show each agent's allowed tools. Say: "An agent cannot call a tool that is not on its list. That is a security boundary, and tests check it."
Say: "The language understanding here is a rule-based classifier, not machine learning. The fraud and loan engines are also rule-based and explainable."

## 2:00 - 2:45 Use case 1: balance
Click the **💬 Chat** tab. **Type:** `What is the account balance for customer C1001?`
Expect: Aarav Mehta, total ₹5,47,250.75 over two accounts, balance table. Open **Execution trace**: intent `ACCOUNT_BALANCE`, agent `BankingAgent`, tools `get_customer` then `get_account_balance`, both success, with durations.

## 2:45 - 3:30 Use case 2: transaction history
**Type:** `Show the last five transactions for customer C1002.`
Expect 5 of 9 transactions, newest first: TXN-9209 down to TXN-9205, with date, amount, merchant, category and status. Mention the extracted entities in the trace: `customer_id=C1002`, `limit=5`.

## 3:30 - 4:30 Use case 3: fraud assessment
**Type:** `Check transaction TXN-9003 for fraud risk.`
Expect: score **95/100**, level **HIGH**, recommended action **ESCALATE**, a red badge and the indicator table (amount 84x the usual debit, ≥ ₹1 lakh, 3 attempts in the last hour, foreign country NG, 02:10, crypto merchant).
Say: "Each signal adds points, so the score is explainable. HIGH means *suspicious*, not *confirmed fraud*, and the simulator takes no action."
Then **Type:** `Is TXN-9004 suspicious?` Expect **MEDIUM (41) → REVIEW**. Contrast with the earlier HIGH.

## 4:30 - 5:30 Use case 4: loan eligibility
**Type:** `Is customer C1001 eligible for a loan of ₹200000?`
Expect: ELIGIBLE (illustrative), EMI about ₹6,547.74, debt-to-income 12.5% now and 18.0% after the loan, a table with four PASS checks.
Say: "The assessment is illustrative with invented thresholds, not a lending decision."
Then **Type:** `Is customer C1003 eligible for a loan of ₹200000?` Expect NOT_ELIGIBLE with reasons (debt-to-income about 63%, credit score 620, short employment).

## 5:30 - 6:30 Use case 5: financial summary (coordinated workflow)
**Type:** `Give me a complete financial summary for customer C1003.`
Expect: balance ₹12,840.10, recent transactions, top-spending chart, credit profile.
Open the trace → **Tool calls**: five sequential calls (`get_customer`, `get_account_balance`, `get_transactions`, `get_loan_profile`, `compute_financial_summary`). Say: "The Banking Agent coordinates several tools and aggregates the result."

## 6:30 - 7:15 Extra scenarios: spending, clarification, unsupported
**Type:** `Show the monthly spending analysis for customer C1002.` Expect ₹26,800 in 2026-09 and the category chart.
**Type (clarification):** `Show my recent transactions` Expect a question asking for the customer ID; no tools in the trace.
**Type (unsupported):** `Transfer ₹5000 from C1001 to C1002` Expect "This simulator is read-only…".

## 7:15 - 7:45 Trace and safety
Say: "The trace is recorded by the running code: real tool calls, statuses, timings, sanitised results. The agent allow-list, parameterised SQL, input validation, and masked contact details are the safety measures."

## 7:45 - 8:15 Tests
In a terminal run `python -m pytest`. Say: "Tests cover classification, entity extraction, tools, fraud and loan scoring, supervisor routing, error containment, LLM-output validation, and all five use cases end to end, including through the real Streamlit UI headlessly."

## 8:15 - 9:00 Limitations, future work, closing
Limitations: rule-based language understanding, illustrative thresholds, small synthetic data, no authentication or consent, not production banking.
Future: a trained intent classifier; evaluating the fraud rules on labelled data against a supervised model; multi-turn memory; production controls.
Close: "A supervisor coordinating specialised agents over allow-listed tools, explainable results, an honest trace, and it all runs locally with no key."

---
*Optional (if Ollama is running):* mention the **LLM mode** badge and that the model's output is validated before use and falls back to rules on any problem.
