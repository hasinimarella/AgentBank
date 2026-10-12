# AgentBank: Simulated Multi-Agent Banking Assistant

> **Everything here is a simulation.** All customers, accounts and transactions are synthetic. The
> "banking APIs" are plain Python functions over a local SQLite file; nothing connects to a real bank.
> No API key, paid service or large model download is required.

A Streamlit chat application in which a **Supervisor agent** understands a natural-language banking
question, validates it, routes it to one of three **specialised agents** (Banking, Fraud, Loan), lets
that agent call **allow-listed simulated banking tools**, and returns a tool-backed answer together with
the **real execution trace** of what ran.

Suggested GitHub description: *Multi-agent banking simulator: supervisor + banking/fraud/loan agents, rule-based NLU, explainable scoring, Streamlit UI.*
Suggested topics: `multi-agent`, `streamlit`, `python`, `fintech`, `fraud-detection`, `agentic-ai`, `pytest`, `ollama`.

---

## 1. Problem statement
Banking requests (balance, history, fraud checks, loan questions, summaries) are handled by different
specialists in real organisations. This project shows how a supervisor can coordinate several focused agents,
each with its own tools and responsibilities, while staying **explainable, testable and safe**.

## 2. Objectives
- Demonstrate genuine modular orchestration (supervisor, router, agents, tool layer, trace), not one chatbot with three labels.
- Provide explainable, deterministic scoring for fraud risk and loan eligibility.
- Work fully offline with zero cost; optionally add a local LLM without changing business logic.
- Be honest about what is rule-based, what is simulated and what would be needed for production.

## 3. Main features
- Seven intents: `ACCOUNT_BALANCE`, `TRANSACTION_HISTORY`, `FRAUD_ASSESSMENT`, `LOAN_ELIGIBILITY`, `CUSTOMER_FINANCIAL_SUMMARY`, `SPENDING_ANALYSIS`, `UNKNOWN`.
- Clarification questions when information is missing; clear messages for unknown IDs and unsupported requests.
- Fraud risk score 0-100 with LOW / MEDIUM / HIGH levels, contributing signals and an ALLOW / REVIEW / ESCALATE recommendation.
- Illustrative loan assessment with EMI, debt-to-income, credit-score, employment and loan-size checks.
- Execution trace per request: trace ID, intent, entities, agent, every tool call with status/duration, sanitised results.
- UI: chat, example buttons, balance/transaction tables, risk badges, loan calculation tables, charts, architecture view, agent descriptions, reset.
- Per-agent tool allow-lists, parameterised SQL, input sanitisation, secrets kept out of logs.

## 4. Technology stack
| Part | Choice |
|---|---|
| Language | Python 3.11 - 3.13 (developed and tested on 3.13) |
| UI | Streamlit 1.65.0 |
| Data | SQLite (standard library `sqlite3`), reproducible synthetic seed |
| Validation | pydantic 2.14.0 |
| Tables / charts | pandas 3.0.6 + Streamlit native charts |
| Optional LLM | Ollama over HTTP via `requests` 2.34.2 (no SDK, no key) |
| Config | environment variables + `.env` via python-dotenv 1.2.4 |
| Tests | pytest 9.1.1 |

All versions are pinned in `requirements.txt`. Nothing in the base install needs a key, a cloud service or a model.

## 5. Architecture overview
```
User -> Streamlit chat UI -> Supervisor
          1. sanitise input
          2. classify intent + extract entities   (local rules; optional LLM, validated)
          3. validate required info / ask a clarifying question
          4. route to ONE specialised agent       (AgentRouter)
          5. agent calls allow-listed tools       (AgentToolbox: permission check, timing, error boundary)
          6. build tool-backed response + record trace
       -> Banking Agent | Fraud Agent | Loan Agent
       -> Simulated banking tools -> SQLite synthetic dataset
```
Full diagrams (Mermaid), sequence charts and design rationale: [ARCHITECTURE.md](ARCHITECTURE.md).

## 6. Multi-agent workflow and responsibilities
| Agent | Handles | Tools it may call |
|---|---|---|
| **Supervisor** | understand, validate, clarify, route, aggregate, trace, error handling | none directly |
| **BankingAgent** | balance, transactions, spending analysis, financial summary (composite, 5 sequential tool calls) | `get_customer`, `get_account_balance`, `get_transactions`, `get_transaction`, `get_spending_analysis`, `get_loan_profile`, `compute_financial_summary` |
| **FraudAgent** | rule-based fraud-risk assessment of one transaction | `get_transaction`, `calculate_fraud_risk` |
| **LoanAgent** | illustrative loan eligibility | `get_customer`, `get_loan_profile`, `assess_loan_eligibility` |

An agent that tries to call a tool outside its list is blocked, and the blocked attempt appears in the trace.

## 7. Simulated banking APIs and tools (`tools/`)
Read-only functions returning `{"ok": true, "data": ...}` or `{"ok": false, "error": {"code", "message"}}`.

| Function | Alias used in the assignment text |
|---|---|
| `get_customer(customer_id)` | |
| `get_account_balance(customer_id)` | |
| `get_transactions(customer_id, limit, status, start_date, end_date, transaction_id)` | |
| `get_transaction(transaction_id)` | |
| `calculate_fraud_risk(transaction_id)` | `assess_transaction_risk` |
| `assess_loan_eligibility(customer_id, requested_amount)` | `evaluate_loan_eligibility` |
| `get_financial_summary(customer_id)` | `get_customer_financial_summary` |
| `get_spending_analysis(customer_id, month)`, `get_loan_profile(customer_id)`, `compute_financial_summary(...)` | |

## 8. Natural-language approach (works without any LLM)
`llm/fallback_provider.py` is a **local rule-based intent classifier**: ordered regular-expression rules
(actions are refused first, then fraud, loan, summary, spending, balance, transactions). `llm/entities.py`
extracts customer IDs (`C1001`, `customer 1001`), transaction IDs (`TXN-9003`, `TXN 9003`), loan amounts
(`₹200000`, `Rs 2,00,000`, `2 lakh`, `50k`, `75000 rupees`), counts (`last five`), months (`September 2026`),
status and dates.
*Benefits:* instant, free, deterministic, explainable, testable. *Limits:* it only knows the phrasings it has
rules for; unusual wording becomes `UNKNOWN`. It is **not** machine learning.

**Optional LLM mode.** If a local Ollama server is reachable and the configured model is installed, the model is
used for intent/entity understanding. Its JSON output is untrusted: it is schema-validated and *grounded*
(an ID the user did not type is rejected). Any failure (timeout, malformed JSON, wrong schema, server down) falls
back to the rules for that request and is shown in the UI/trace. The mode indicator never claims an LLM that is not
actually active. Banking numbers always come from tools, never from the model.

## 9. Fraud-scoring algorithm (`tools/fraud_tools.py`)
A transparent weighted-rule engine, **not a trained ML model**. Score = sum of triggered indicators (max 100).

| Indicator (max points) | Rule |
|---|---|
| unusual_amount (25) | amount / customer's median earlier completed debit: >=10x = 25, >=5x = 18, >=3x = 10 |
| high_absolute_amount (15) | >= 100,000 = 15; >= 50,000 = 8 |
| velocity (20) | other transactions in the preceding 60 min: >=3 = 20, 2 = 12, 1 = 5 |
| unusual_location (20) | different country from home = 20; first time in another city of the home country = 8 |
| odd_hours (5) | 23:00-04:59 |
| risky_merchant_category (10) | CRYPTO, GIFT_CARDS, GAMBLING, WIRE_TRANSFER |
| transaction_status (5) | FAILED = 5, PENDING = 2 |

Levels (configurable): **LOW** < 30, **MEDIUM** 30-59, **HIGH** >= 60 → recommended action **ALLOW / REVIEW / ESCALATE**.
A HIGH score means *suspicious, worth human review*, never "confirmed fraud". The simulator freezes nothing and blocks nothing.
The scorer sits behind a `RiskScorer` protocol so a trained model could replace it later.
*Limitations:* hand-set weights, no labelled evaluation, tiny synthetic history, no device/IP/behavioural data.

## 10. Loan-eligibility algorithm (`tools/loan_tools.py`)
Deterministic and illustrative. With assumed rate `r = 11%/12` and tenure `n = 36` months:

```
EMI            = P * r * (1+r)^n / ((1+r)^n - 1)
DTI before     = existing monthly debt / monthly income
DTI after loan = (existing monthly debt + EMI) / monthly income
```
| Check | PASS | REFER | FAIL |
|---|---|---|---|
| credit score | >= 650 | 600-649 | < 600 |
| DTI after loan | <= 40% | 40-50% | > 50% |
| employment | >= 1 year | - | < 1 year |
| amount vs annual income | <= 2x | - | > 2x |

Any FAIL → `NOT_ELIGIBLE`; else any REFER → `REFER_TO_REVIEW`; else `ELIGIBLE`. Missing income/debt/credit/employment →
`INSUFFICIENT_DATA` (nothing is assumed). Amounts outside 10,000-5,000,000 are rejected. All thresholds are environment-configurable.
It is **not** a credit-scoring model and not a lending decision.

## 11. Supported use cases and sample prompts
| # | Prompt | Result with the seeded data |
|---|---|---|
| 1 | `What is the account balance for customer C1001?` | ₹5,47,250.75 over 2 accounts → BankingAgent |
| 2 | `Show the last five transactions for customer C1002.` | TXN-9209 … TXN-9205 → BankingAgent |
| 3 | `Check transaction TXN-9003 for fraud risk.` | 95/100, HIGH, ESCALATE → FraudAgent |
| 4 | `Is customer C1001 eligible for a loan of ₹200000?` | ELIGIBLE (illustrative), EMI ₹6,547.74, DTI 12.5% → 18.0% → LoanAgent |
| 5 | `Give me a complete financial summary for customer C1003.` | 5 sequential tools → BankingAgent |
| 6 | `Show the monthly spending analysis for customer C1002.` | ₹26,800.00 in 2026-09 by category + chart |
| 7 | `Show my recent transactions.` | asks for the customer ID (clarification) |
| 8 | `Transfer ₹5000 from C1001 to C1002.` | refused: the simulator is read-only |

More: `Is TXN-9004 suspicious?` (MEDIUM), `Can customer C1002 borrow ₹6 lakh?` (REFER_TO_REVIEW),
`Is customer C1005 eligible for a loan of ₹200000?` (INSUFFICIENT_DATA), `Show the transactions for customer C1006.` (empty history).

## 12. Sample IDs
| Customer | Name | Profile |
|---|---|---|
| C1001 | Aarav Mehta | strong profile; two accounts |
| C1002 | Priya Nair | 9 transactions; ₹6 lakh loan needs review |
| C1003 | Rohan Das | heavy debt; loan not eligible |
| C1004 | Sneha Iyer | owns the suspicious transactions |
| C1005 | Vikram Singh | income not on file; dormant account |
| C1006 | Ananya Rao | new customer, no transactions |

Transactions: `TXN-9003` HIGH (95), `TXN-9010` HIGH (65), `TXN-9004` MEDIUM (41), `TXN-9102` LOW (0). Unknown-ID demos: `C9999`, `TXN-0000`.

## 13. Folder structure
```
agentbank-mvp/
├── app.py                  Streamlit UI
├── start.bat / start.sh    one-command startup (Windows / macOS-Linux)
├── requirements.txt  .env.example  .gitignore  LICENSE  pytest.ini  .streamlit/config.toml
├── README.md  ARCHITECTURE.md  DEMO_SCRIPT.md
├── agents/        supervisor.py  banking_agent.py  fraud_agent.py  loan_agent.py  base.py
├── llm/           base.py (intents, schema, validation)  entities.py (entity extraction)
│                  fallback_provider.py (local rule-based classifier)  ollama_provider.py
│                  openai_compatible_provider.py (optional)  factory.py
├── tools/         banking_tools.py  fraud_tools.py  loan_tools.py  common.py
├── services/      router.py  tool_executor.py  response_builder.py  audit_service.py
├── config/        settings.py
├── database/      db.py  schema.sql
├── data/          seed_data.py   (deterministic synthetic data → SQLite)
├── tests/         unit, agent, LLM-validation, integration and UI tests
└── docs/          architecture_notes.md  design_decisions.md  demo_checklist.md
```
Synthetic data lives in `data/seed_data.py` and is written to a SQLite file (`var/agentbank.db`, created automatically and git-ignored).

## 14. Windows installation and run
**Easiest:** extract the ZIP, open the folder, double-click **`start.bat`**. It checks for Python 3.11+, creates `.venv`,
installs `requirements.txt`, creates the database and starts the app. Then open **http://localhost:8501**.

**Manual (PowerShell)**, from the project folder:
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1        # if blocked: Set-ExecutionPolicy -Scope Process Bypass
python -m pip install -r requirements.txt
python -m data.seed_data
python -m streamlit run app.py
```
**Manual (Command Prompt):** use `.venv\Scripts\activate.bat` instead of the `Activate.ps1` line.
**macOS / Linux:** `./start.sh`, or `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python -m data.seed_data && python -m streamlit run app.py`.

Python 3.11 or newer is required: https://www.python.org/downloads/ (tick "Add python.exe to PATH").

## 15. Running the tests
```powershell
python -m pytest
```
Tests use deterministic seeded data. The LLM tests talk over real HTTP to a small local **scripted** server (`tests/fake_llm_server.py`):
they verify the provider code, validation, grounding and fallback, **not** the quality of a real model. UI tests drive the real Streamlit app headlessly.

## 16. Optional: local LLM mode (Ollama)
The app works fully without this. To try it: install Ollama (https://ollama.com), then
```powershell
ollama pull llama3.2:3b
copy .env.example .env      # then keep LLM_PROVIDER=auto (default) and OLLAMA_MODEL=llama3.2:3b
```
Restart the app (or press **Re-check LLM availability**). The sidebar shows **LLM mode** only if the server answered *and* the model is installed;
otherwise it shows **Fallback mode** with the reason. Any model name can be set with `OLLAMA_MODEL`; `LLM_PROVIDER=fallback` forces rules only.
`LLM_PROVIDER=openai_compatible` supports any OpenAI-style endpoint (`OPENAI_COMPAT_*` variables). Answer quality of any particular model is not guaranteed.

## 17. Troubleshooting
| Symptom | Fix |
|---|---|
| `Python was not found` / Microsoft Store opens | Install Python 3.11+ from python.org and tick "Add to PATH"; or disable the Store alias in *Settings → Apps → App execution aliases* |
| PowerShell: *running scripts is disabled* | `Set-ExecutionPolicy -Scope Process Bypass`, then activate again (or use Command Prompt) |
| `ModuleNotFoundError: agents` / `llm` | Run commands from the project root (the folder containing `app.py`) |
| `pip install` fails | Check internet/proxy; upgrade pip: `python -m pip install --upgrade pip` |
| Port 8501 in use | `python -m streamlit run app.py --server.port 8502` |
| Database looks wrong | `python -m data.seed_data --reset` |
| Sidebar says Fallback mode but I installed Ollama | Start Ollama, check `OLLAMA_MODEL` matches `ollama list`, press *Re-check LLM availability* |

## 18. Current limitations
- Rule-based NLU only understands the phrasings it has rules for. One customer/transaction per message, one agent per request.
- Fraud and loan engines use hand-set, illustrative thresholds, not validated against labelled data.
- Synthetic data is small (6 customers, 31 transactions) and fixed in time.
- No authentication, authorisation or consent: any user can query any synthetic customer.
- `start.bat` was written for Windows but the project was built and tested on Linux, where only the equivalent steps (`start.sh` / manual commands) could be run. If anything fails on Windows, use the manual PowerShell steps above and please report it.
- LLM mode was verified only against a scripted local test server in the build environment, not against a real model.

## 19. Future enhancements
- Replace the rule-based classifier with a **trained intent classifier** (labelled utterances, train/validation split, accuracy/F1, keep rules as fallback).
- Evaluate the fraud rules on a **labelled dataset** (precision/recall, thresholds by cost), compare with a supervised model (e.g. gradient boosting) using the same `RiskScorer` interface.
- Multi-turn memory ("what about their loan?"), multiple agents per request, richer charts, an audit-log viewer.
- Production controls: see the section below.

## 20. Security and synthetic-data disclaimer
Prototype-level safeguards: input sanitisation and length cap, strict ID/amount/limit validation, parameterised SQL only, per-agent tool allow-lists,
validated and grounded LLM output, no model-generated code or SQL, secrets only from environment variables and never logged, contact details masked/redacted.
The simulator performs no transfers, payments, freezes or approvals. **Not production banking software.** A real system would additionally need
authentication and authorisation, customer consent, encryption in transit and at rest, tamper-evident audit logs, monitoring and alerting,
regulatory compliance (e.g. KYC/AML, data-protection law), model governance and human review of fraud and credit decisions.

## 21. Publish to GitHub
```bash
git init
git add .
git commit -m "Initial commit: AgentBank multi-agent banking simulator"
git branch -M main
git remote add origin https://github.com/<your-username>/agentbank-mvp.git
git push -u origin main
```
Create the empty repository on GitHub first and replace `<your-username>`. `.env`, `.venv/`, caches and the generated database are git-ignored.

## 22. Documentation map
[ARCHITECTURE.md](ARCHITECTURE.md) · [DEMO_SCRIPT.md](DEMO_SCRIPT.md) · [docs/architecture_notes.md](docs/architecture_notes.md) · [docs/design_decisions.md](docs/design_decisions.md) · [docs/demo_checklist.md](docs/demo_checklist.md)

License: MIT (see `LICENSE`).
