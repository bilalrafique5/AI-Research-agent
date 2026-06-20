#  AI Research Agent

A multi-agent AI system that plans, researches, summarizes, writes, **critiques**, and regenerates its own research reports — then exports them as PDFs and lets you chat with them using RAG-based Q&A.

Built with **FastAPI**, **Groq (Llama 3.3)**, **Tavily Search**, **MongoDB**, and **HashiCorp Vault** for secrets management.

---

##  Key Features

-  **Multi-Agent Pipeline** — Planner → Search → Summarizer → Report Generator → Critic
-  **Self-Correcting Critic Agent** — scores every report on clarity, accuracy, and completeness, and automatically regenerates it (up to 2x) if it doesn't meet quality thresholds
-  **Live Web Search** — powered by Tavily, with graceful fallback to a knowledge-based response if search fails or is disabled
-  **PDF Report Generation** — every research run is exported as a downloadable PDF
-  **RAG-Based Chat (Q&A over PDFs)** — ask follow-up questions about any generated report; answers are retrieved using TF-IDF + cosine similarity over chunked PDF text
-  **JWT Authentication** — Argon2 password hashing, Bearer token-protected endpoints
-  **Vault-Backed Secrets** — API keys, DB URLs, and feature flags are pulled live from HashiCorp Vault, with hot-reloading every 30 seconds
-  **Per-User History** — research history and chat sessions stored in MongoDB

---

##  Architecture

```
User Query
    │
    ▼
┌─────────────┐
│   Planner   │  → breaks the query into actionable research steps
└──────┬──────┘
       ▼
┌─────────────┐
│ Search Agent│  → fetches live results via Tavily (falls back gracefully)
└──────┬──────┘
       ▼
┌─────────────┐
│ Summarizer  │  → extracts key topics with confidence scores + sources
└──────┬──────┘
       ▼
┌─────────────┐
│   Report    │  → structures everything into a polished report
└──────┬──────┘
       ▼
┌─────────────┐
│   Critic    │  → scores clarity / accuracy / completeness
└──────┬──────┘
       │  fails threshold?  ──► regenerate (max 2x)
       ▼
┌─────────────┐
│  PDF Export │  → saved to /reports, downloadable via API
└─────────────┘
       │
       ▼
┌──────────────────────┐
│  RAG Chat Engine      │  → chunk PDF → TF-IDF index → answer follow-up Qs
└──────────────────────┘
```

---

##  Project Structure

```
ai_research_agent/
├── agents/                # Individual AI agents (LLM-powered)
│   ├── planner.py         # Breaks query into steps
│   ├── search.py          # Wraps the search tool
│   ├── summarizer.py      # Summarizes with confidence scores
│   ├── report.py          # Generates structured report
│   ├── critic.py          # Evaluates report quality
│   └── qa_agent.py        # Answers questions using RAG context
│
├── api/                   # FastAPI route handlers
│   ├── auth.py             # /auth/register, /auth/login
│   ├── routes.py           # /api/research, history, PDF download
│   ├── chat.py              # /api/chat/* — RAG Q&A endpoints
│   └── dependencies.py      # JWT auth dependency (get_current_user)
│
├── config/                 # App configuration
│   ├── database.py          # MongoDB connection & index setup
│   └── secret_manager.py     # HashiCorp Vault integration
│
├── models/                  # Pydantic schemas
│   ├── user.py                # User register/login/token models
│   └── chat.py                 # Chat message/session models
│
├── services/
│   └── workflow.py             # Orchestrates the full agent pipeline
│
├── tools/
│   ├── search_tools.py          # Tavily web search wrapper
│   ├── rag_engine.py            # PDF chunking + TF-IDF retrieval
│   └── pdf_generator.py         # Builds the PDF report
│
├── utils/
│   └── auth.py                   # Password hashing & JWT helpers
│
├── reports/                       # Generated PDF reports (output)
├── main.py                        # FastAPI app entrypoint
└── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MongoDB (local or Atlas)
- HashiCorp Vault (dev mode is fine for local development)
- API keys for [Groq](https://console.groq.com) and [Tavily](https://tavily.com)

### 1. Clone the repository

```bash
git clone https://github.com/bilalrafique5/AI-Research-agent.git
cd AI-Research-agent
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

> **Note:** `hvac` (the Vault client library) is required but may need to be installed separately:
> ```bash
> pip install hvac
> ```

### 3. Start MongoDB

```bash
mongod
```

Or use a MongoDB Atlas connection string instead of a local instance.

### 4. Start Vault (dev mode) and load secrets

```bash
vault server -dev
```

In a **new terminal**, using the root token printed by the dev server:

```powershell
$env:VAULT_ADDR = "http://127.0.0.1:8200"
$env:VAULT_TOKEN = "your-dev-root-token"

vault kv put secret/ai-research-agent MONGODB_URL="mongodb://localhost:27017" DATABASE_NAME="ai_research_agent" SECRET_KEY="a-long-random-secret" GROQ_API_KEY="your-groq-key" TAVILY_API_KEY="your-tavily-key" TAVILY_SEARCH_ENABLED="true"
```

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Set Vault connection details for the app

Create a `.env` file in the project root with at least:

```env
VAULT_ADDR=http://127.0.0.1:8200
VAULT_TOKEN=your-dev-root-token
```

All other secrets (DB URL, API keys, JWT secret) are pulled from Vault at startup — not from `.env` directly.

### 6. Run the server

```bash
uvicorn main:app --reload
```

The API will be live at **http://127.0.0.1:8000**, with interactive docs at **http://127.0.0.1:8000/docs**.

---

##  API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive a JWT access token |

### Research

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/research` | Run the full agent pipeline on a query |
| `GET` | `/api/research-history` | Get the current user's past research |
| `GET` | `/api/download-report/{filename}` | Download a generated PDF report |

### Chat (RAG Q&A)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat/ask` | Ask a question about a specific PDF report |
| `GET` | `/api/chat/history` | Get chat history for a PDF |
| `GET` | `/api/chat/sessions` | List all chat sessions for the user |
| `DELETE` | `/api/chat/session` | Delete a chat session |

All `/api/*` endpoints require a Bearer token from `/auth/login` in the `Authorization` header.

### Example: Run a research query

```bash
curl -X POST http://127.0.0.1:8000/api/research \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "Latest trends in AI agents"}'
```

---

##  Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| LLM Inference | Groq (Llama 3.3 70B) |
| Web Search | Tavily |
| Database | MongoDB |
| Secrets Management | HashiCorp Vault |
| Auth | JWT (python-jose) + Argon2 |
| RAG Retrieval | scikit-learn (TF-IDF + cosine similarity) |
| PDF Generation | ReportLab |
| PDF Parsing | PyPDF2 |

---

##  Security Notes

- Passwords are hashed with **Argon2**, not stored in plaintext.
- JWT tokens are required on all research and chat endpoints.
- Secrets (API keys, DB credentials, JWT signing key) are centrally managed via Vault and never hardcoded — **make sure to set a real `SECRET_KEY`** in Vault rather than relying on any default value.
- CORS is currently configured permissively for local development — restrict `allow_origins` before deploying publicly.

See [`SECURITY.md`](./SECURITY.md) for more details.

---

##  Roadmap

- [ ] Rate limiting on auth endpoints
- [ ] Replace TF-IDF retrieval with embedding-based vector search
- [ ] Structured (JSON-mode) output for the critic agent
- [ ] Automated test suite
- [ ] Dockerized deployment

---

##  License

This project is currently unlicensed. Add a `LICENSE` file if you intend to open-source it.

---

##  Author

Built by [Bilal Rafique](https://github.com/bilalrafique5).