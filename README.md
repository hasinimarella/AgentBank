# 🏦 AgentBank — AI-Powered Banking Assistant

**An interactive banking assistant built with Python and Streamlit**

AgentBank is a prototype banking assistant that provides a conversational interface for common banking-related queries. It supports account balance inquiries, transaction history, transaction fraud-risk checks, and loan eligibility queries through an interactive web application.

The project demonstrates how a user-friendly interface and agent-based request processing can simplify access to banking information using synthetic demonstration data.

---

## 📌 1. Project Overview

Traditional banking applications often require users to navigate multiple screens to find information or complete simple inquiries. AgentBank explores an alternative approach by allowing users to submit banking-related requests through a conversational interface.

The application accepts a user's question, processes supported requests through the existing application logic, and presents the result through a Streamlit interface.

**Project type:** AI-assisted banking application prototype  
**Domain:** Banking and financial technology  
**Primary language:** Python  
**User interface:** Streamlit

## 🎯 2. Problem Statement

Users may need to navigate multiple interfaces to check account information, review transactions, or understand banking-related assessments.

The objective of AgentBank is to demonstrate a simpler interaction model in which users can request supported banking information using natural-language prompts and receive responses through one interface.

## 🎯 3. Project Objectives

- Develop a simple and interactive banking assistant.
- Provide a conversational interface for supported banking queries.
- Demonstrate account balance and transaction information retrieval.
- Implement demonstration workflows for transaction fraud-risk assessment and loan eligibility.
- Organize request processing using the supervisor, agents, and tools available in the project.
- Present responses through a user-friendly Streamlit application.

## ✨ 4. Key Features

| Feature | Description |
|---|---|
| Account Balance | Retrieves balance information for a supported customer query. |
| Transaction History | Displays recent transaction information. |
| Fraud Risk Check | Processes a transaction fraud-risk inquiry using the project's existing logic. |
| Loan Eligibility | Evaluates a loan-related query using the implemented demonstration workflow. |
| Conversational Interface | Allows users to interact with the application using prompts. |
| Quick Prompts | Provides predefined queries for common tasks. |
| Request Processing | Uses the existing supervisor, agents, and tools to handle supported requests. |

## ⚙️ 5. System Implementation

The application is implemented in Python, with Streamlit providing the interactive web interface.

### Request-processing workflow

1. **User input:** The user enters a banking-related question or selects a quick prompt.
2. **Request handling:** The application receives the submitted request.
3. **Request processing:** The existing supervisor, agents, and tools process the supported query.
4. **Result generation:** The relevant application logic produces a response based on the available demonstration data.
5. **Response display:** The interface presents the response to the user.

### High-level workflow

```text
User
  |
  v
Streamlit Interface
  |
  v
Request Handling
  |
  v
Supervisor / Agent Processing
  |
  v
Relevant Tool or Application Logic
  |
  v
Result Generation
  |
  v
Response Displayed to User
```

This diagram represents the high-level request flow. The exact agent selection, tool execution, and data-handling behavior depend on the project's implementation.

## 🛠️ 6. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application and request-processing logic |
| Streamlit | Interactive web interface |
| Existing agent and tool modules | Processing supported banking requests |
| Git and GitHub | Source-code version control and project hosting |

Add any additional AI models, frameworks, databases, or APIs only if they are actually used in your implementation.

## 🖥️ 7. Application Screenshots

Screenshots of the running application will help readers understand the interface without installing the project.

### Home Page

<img width="1917" height="913" alt="image" src="https://github.com/user-attachments/assets/55e7fcf8-e25f-4368-b8fa-575ec2142df3" />


### Banking Query Response
<img width="1917" height="915" alt="Screenshot 2026-10-12 152655" src="https://github.com/user-attachments/assets/0f26f6cd-f81c-476f-87ad-3a4391bdfcc2" />
<img width="1537" height="775" alt="Screenshot 2026-10-12 152559" src="https://github.com/user-attachments/assets/28e4c27e-6aaf-4ef2-9db7-91490dd935ac" />
<img width="1447" height="756" alt="Screenshot 2026-10-12 152458" src="https://github.com/user-attachments/assets/658f200f-8f97-4951-aaa1-1466f76bf8da" />
<img width="1917" height="912" alt="Screenshot 2026-10-12 152424" src="https://github.com/user-attachments/assets/3f4090cc-8b41-4379-a9e4-aca4060da760" />
<img width="1407" height="811" alt="Screenshot 2026-10-12 152714" src="https://github.com/user-attachments/assets/a56df563-f43d-4c77-ba18-5be04051fc29" />






**Note:** The above shown outputs are the use-cases that demonstrate the implementation  of the AgentBank

## 🚀 8. Installation and Execution

### Prerequisites

- Python installed on your system
- Git installed on your system
- Access to the project repository

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/AgentBank.git
cd AgentBank
```

Replace `YOUR-USERNAME` with your GitHub username.

### Step 2: Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4: Start the application

```bash
streamlit run app.py
```

Open the local URL printed in the terminal to access AgentBank.

**Note:** These instructions assume the repository contains `app.py` and a complete `requirements.txt`. If your project requires environment variables, API credentials, or additional setup, document those requirements separately without publishing secret values.

## 🧪 9. Example Queries

Users can try the following demonstration queries:

- `What is the account balance for customer C1001?`
- `Show the last five transactions for customer C1002.`
- `Check transaction TXN-9003 for fraud risk.`
- `Is customer C1001 eligible for a loan of ₹200000?`

The availability and output of each query depend on the project's configured demonstration data and processing logic.

## 🎬 10. Project Demo

**Demo Video:** [[Add your project demonstration video link here]](https://drive.google.com/file/d/1qkXmVjjjKIEDBnblxFyywL5anuc6VnNY/view?usp=drivesdk)

The demonstration video should show the home page, a few example queries, the returned responses, and the application's key features.

**GitHub Repository:** [https://github.com/YOUR-USERNAME/AgentBank](https://github.com/hasinimarella/AgentBank.git)

## 🔗 11. Project References and Resources

- **Source Code:** [[AgentBank GitHub Repository](https://github.com/YOUR-USERNAME/AgentBank)](https://github.com/hasinimarella/AgentBank.git)
- **Project Demonstration:** https://drive.google.com/file/d/1qkXmVjjjKIEDBnblxFyywL5anuc6VnNY/view?usp=drivesdk
- **Documentation:** [Streamlit Documentation](https://docs.streamlit.io/)
- **Language Documentation:** [Python Documentation](https://docs.python.org/3/)

Add any research-paper references, project-specific documentation, or external resources used during development here. Clearly distinguish external references from your own implementation.

## 🔐 12. Data Privacy and Limitations

AgentBank is a demonstration prototype that uses synthetic banking data.

- It is not connected to real bank accounts.
- Fraud-risk and loan-eligibility outputs are illustrative and should not be treated as professional financial assessments.
- The application is not intended for production banking use.
- Credentials, API keys, and private customer information must not be committed to the repository.

## 📈 13. Future Enhancements

Potential future improvements include:

- Expanding the supported banking queries.
- Improving request classification and error handling.
- Adding automated tests for the banking workflows.
- Improving logging and monitoring of request execution.
- Introducing secure authentication and authorization for an appropriately designed production system.

These are potential enhancements, not claims about features already implemented.
