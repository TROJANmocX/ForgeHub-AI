<div align="center">

# ⚡ ForgeHub AI

### Metadata-Governed AI Data Engineering Agent

[![CI](https://github.com/TROJANmocX/ForgeHub-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/TROJANmocX/ForgeHub-AI/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-20%20|%2022-green?logo=node.js&logoColor=white)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**ForgeHub AI** connects to **DataHub**, reads verified dataset metadata, enforces symbol table contracts, produces production-ready **dbt models**, tests, and documentation — and writes verified lineage back to DataHub. The LLM is *never trusted* to invent tables or columns. Hallucinated references are rejected mechanically at the AST layer.

> 🚀 **Zero external dependencies in Demo Mode** — runs fully offline with mock LLM and fixture metadata.

[Quick Start](#-quick-start) · [Demo Tour](#-dashboard-tour--demo-flow) · [Architecture](#-architecture) · [Docker Deployment](#-docker-deployment) · [LLM Providers](#-llm-providers) · [API Reference](#-api-reference) · [Contributing](./CONTRIBUTING.md)

</div>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔒 **Symbol Table Contract** | Generation is mechanically constrained to symbols present in DataHub. Hallucinated columns (`UNKNOWN_COLUMN`) or tables (`UNKNOWN_TABLE`) are rejected by `sqlglot` AST validation |
| 🧠 **Semantic Type Safety** | Prevents illegal operations: mixed-currency addition (`USD + EUR`), summing percentages (`SUM(discount_rate)`), or arithmetic on identifier columns |
| 📊 **Metadata Quality Engine** | Scores datasets 0–100 with explicit per-gap breakdowns (Blocking / Warning / Informational) |
| 🔍 **Inspectable Reasoning** | Produces a pre-generation plan with decision evidence and confidence scores *before* any LLM call |
| 🔁 **Self-Repair Loop** | Automatically feeds AST/YAML validation error tracebacks back into the LLM (max `MAX_REPAIR_ATTEMPTS=3`) |
| 📝 **DataHub Write-Back** | Writes model documentation, AI tags (`#ai-generated`, `#forgehub`), and upstream lineage to DataHub |
| 🎭 **Demo Mode** | Fully functional offline with zero external API keys |
| 💥 **Failure Demo** | Built-in "Break It" feature demonstrates real-time contract rejection of hallucinated SQL |

---

## 🏗️ Architecture

```
DataHub Metadata / Fixtures
       ↓
┌─────────────────────────────┐
│     Metadata Agent          │  → Fetches & normalises DataHub metadata
│     + Symbol Table Builder  │  → Constructs the verified symbol contract
└─────────────────────────────┘
       ↓
┌─────────────────────────────┐
│     Quality Agent           │  → Scores 0–100, detects blocking gaps
└─────────────────────────────┘
       ↓
┌─────────────────────────────┐
│     Reasoning Agent         │  → Deterministic plan: grain, transforms, tests
└─────────────────────────────┘
       ↓
┌─────────────────────────────┐
│     Generation Agent        │  → Calls LLM via provider abstraction
│     + Self-Repair Loop      │  → Re-prompts with errors (max 3 attempts)
└─────────────────────────────┘
       ↓ (SQL + schema.yml + README.md)
┌─────────────────────────────────────────────────────┐
│                  Validation Layer                   │
│  ├── AST Validator (sqlglot) — symbol table check  │
│  ├── Semantic Type Validator — currency/pct/id      │
│  └── dbt YAML Validator — schema contract           │
└─────────────────────────────────────────────────────┘
       ↓
┌─────────────────────────────┐
│  Human Approval & Governance│
└─────────────────────────────┘
       ↓
┌─────────────────────────────┐
│  DataHub Write-Back         │  → Lineage, tags, documentation
└─────────────────────────────┘
```

### LLM Provider Abstraction

```
LLMProvider (base)
├── MockProvider        — deterministic, zero API keys, demo mode
├── ClaudeProvider      — Anthropic claude-3-5-sonnet
├── OpenAIProvider      — OpenAI gpt-4o
└── GeminiProvider      — Google gemini-1.5-pro
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.11+ (3.12 recommended) |
| Node.js | 18+ (20 or 22 recommended) |
| npm | 8+ |

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/forgehub-ai.git
cd forgehub-ai
```

### 2. Environment Setup

```bash
cp .env.example .env
```

The default `.env` enables **Demo Mode** (`DEMO_MODE=true`, `LLM_PROVIDER=mock`) — no external dependencies required.

### 3. Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

FastAPI server: `http://localhost:8000`  
Interactive API docs: `http://localhost:8000/docs`

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

---

## 🐳 Docker Deployment

Run the entire stack with a single command — no Python or Node needed on the host.

```bash
# 1. Copy and configure environment
cp .env.example .env

# 2. Build and start all services
docker compose up --build

# Dashboard → http://localhost:80
# API       → http://localhost:8000
# API Docs  → http://localhost:8000/docs
```

### Docker Compose Services

| Service | Image | Port |
|---------|-------|------|
| `backend` | Python 3.12 slim + FastAPI | `8000` |
| `frontend` | Node 22 build → Nginx 1.27 | `80` |

### Customise Ports

```bash
BACKEND_PORT=9000 FRONTEND_PORT=3000 docker compose up
```

### Stop / Remove

```bash
docker compose down           # stop containers
docker compose down -v        # also remove volumes
```

---

## 🎨 Dashboard Tour & Demo Flow

1. **Select Dataset**: Click `retail.orders` in the left catalog sidebar.
2. **Inspect Quality & Gaps**: Observe the quality score **82/100** and blocking gap: `UNDEFINED_CURRENCY — unit_price currency unit not specified`.
3. **Generate Model**: Click **Generate dbt Model**. Watch the structured reasoning plan materialise, followed by `model.sql`, `schema.yml`, and `README.md`.
4. **Validation Checklist**: Verify green checkmarks for SQL Syntax, Table References, Column References, Semantic Safety, dbt Schema, and Tests.
5. **Demonstrate Failure (Break It)**: Click **Failure Demo (Break It)** to see the AST contract reject hallucinated columns (`customer_name`, `fake_revenue`).
6. **Publish to DataHub**: Click **Approve & Publish to DataHub** to trigger lineage graph write-back (`retail.orders → forgehub.fct_orders`).

### Available Demo Datasets

| Dataset | Model Generated | Quality Score | Notable Gap |
|---------|----------------|---------------|-------------|
| `retail.orders` | `fct_orders` | 82/100 | `UNDEFINED_CURRENCY` on `unit_price` (blocking) |
| `retail.customers` | `dim_customers` | 75.5/100 | `AMBIGUOUS_SEMANTIC_TYPE` on `country_code`, `MISSING_PII_CLASSIFICATION` on `email` |
| `retail.revenue` | `monthly_revenue` | 68/100 | 2× `UNDEFINED_CURRENCY` — `gross_revenue`, `discount_amount` (both blocking) |

---

## 🔑 LLM Providers

Switch providers by setting environment variables — no code changes needed.

### Mock (Default — Zero Cost)

```env
DEMO_MODE=true
LLM_PROVIDER=mock
```

Returns pre-baked, deterministic dbt artifacts. Fully functional offline.

### Anthropic Claude

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
DEMO_MODE=false
```

Uses `claude-3-5-sonnet-20241022` by default.

```bash
pip install anthropic
```

### OpenAI GPT-4o

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
DEMO_MODE=false
```

Uses `gpt-4o` by default.

```bash
pip install openai
```

### Google Gemini

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
DEMO_MODE=false
```

Uses `gemini-1.5-pro` by default.

```bash
pip install google-generativeai
```

> **Note**: When `DEMO_MODE=true`, the mock provider is always used regardless of `LLM_PROVIDER`.

---

## 📁 Repository Structure

```
forgehub-ai/
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions: test + build + Docker
│
├── backend/
│   ├── app/
│   │   ├── agents/             # Metadata, Quality, Reasoning, Generation agents
│   │   │   ├── generation_agent.py
│   │   │   ├── metadata_agent.py
│   │   │   ├── quality_agent.py
│   │   │   └── reasoning_agent.py
│   │   ├── api/                # FastAPI routers
│   │   │   ├── datasets.py     # GET /datasets, GET /datasets/{id}
│   │   │   ├── generation.py   # POST /generate
│   │   │   ├── publish.py      # POST /publish
│   │   │   └── validation.py   # POST /validate
│   │   ├── datahub/            # DataHub client + fixtures + write-back
│   │   │   ├── client.py
│   │   │   ├── fixtures/       # Demo JSON metadata (orders, customers, revenue)
│   │   │   ├── metadata.py
│   │   │   └── writeback.py
│   │   ├── llm/                # LLM provider abstraction
│   │   │   ├── base.py
│   │   │   ├── claude.py
│   │   │   ├── gemini.py
│   │   │   ├── mock.py
│   │   │   └── openai.py
│   │   ├── models/             # Pydantic models
│   │   │   ├── artifacts.py
│   │   │   ├── generation.py
│   │   │   ├── metadata.py
│   │   │   └── reasoning.py
│   │   ├── validation/         # AST + Semantic + dbt YAML validators
│   │   │   ├── dbt_validator.py
│   │   │   ├── semantic_validator.py
│   │   │   └── sql_validator.py
│   │   ├── config.py           # Pydantic settings
│   │   └── main.py             # FastAPI app entry point
│   ├── tests/                  # pytest test suite (52 tests)
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts       # REST API client with fallback demo
│   │   ├── components/         # React components (13)
│   │   ├── types/
│   │   │   └── index.ts        # TypeScript interfaces
│   │   ├── App.tsx             # Root app + routing logic
│   │   └── index.css           # Global styles
│   ├── Dockerfile
│   ├── nginx.conf              # Production Nginx config
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml          # Full-stack Docker Compose
├── .env.example                # Template — copy to .env
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```

---

## 🔌 API Reference

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### `GET /datasets`

List all available datasets.

**Response**
```json
[
  {
    "id": "orders",
    "name": "retail.orders",
    "platform": "bigquery",
    "environment": "PROD",
    "description": "Raw orders transactional table..."
  }
]
```

---

### `GET /datasets/{dataset_id}`

Full metadata and quality report for a dataset.

**Path parameter**: `dataset_id` — e.g. `orders`, `customers`, `revenue`

**Response** (abbreviated)
```json
{
  "id": "orders",
  "name": "retail.orders",
  "quality": {
    "overall_score": 82.0,
    "dimensions": [...],
    "gaps": [
      {
        "type": "UNDEFINED_CURRENCY",
        "asset": "retail.orders.unit_price",
        "severity": "blocking",
        "reason": "Column 'unit_price' appears to be a monetary value but has no currency unit defined.",
        "generation_impact": "Cannot safely perform cross-currency financial aggregation."
      }
    ],
    "blocking_count": 1
  }
}
```

---

### `POST /generate`

Run the full ForgeHub AI pipeline.

**Request body**
```json
{
  "dataset_id": "orders",
  "model_name": null,
  "broken_mode": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `dataset_id` | string | Dataset ID to generate a model for |
| `model_name` | string? | Override the auto-inferred dbt model name |
| `broken_mode` | boolean | Set `true` to trigger hallucination failure demo |

**Response** (abbreviated)
```json
{
  "run_id": "f3a1b2c4-...",
  "status": "REQUIRES_REVIEW",
  "model_name": "fct_orders",
  "sql": "WITH orders AS (...)\nSELECT * FROM final",
  "schema_yml": "version: 2\n...",
  "readme": "# fct_orders\n...",
  "validation": {
    "passed": true,
    "checks": [
      { "name": "SQL Syntax", "passed": true },
      { "name": "Column References", "passed": true },
      { "name": "Semantic Checks", "passed": true }
    ],
    "errors": [],
    "warnings": ["UNDEFINED_CURRENCY warning: unit_price"]
  },
  "reasoning_plan": {
    "model_name": "fct_orders",
    "grain": "One row per unique (order_id)",
    "transformations": [...]
  },
  "repair_attempts": 0,
  "llm_provider": "mock",
  "blocking_gaps": ["Column 'unit_price' appears to be a monetary value but has no currency unit defined."]
}
```

**Status values**

| Status | Meaning |
|--------|---------|
| `VALIDATED` | All checks pass, no blocking gaps |
| `REQUIRES_REVIEW` | Checks pass but blocking metadata gaps exist |
| `FAILED` | AST, semantic, or schema validation failed |

---

### `POST /validate`

Validate arbitrary SQL and schema YAML against a dataset's symbol table.

**Request body**
```json
{
  "dataset_id": "orders",
  "sql": "SELECT order_id, customer_id FROM retail.orders",
  "schema_yml": "version: 2\nmodels:\n  - name: my_model",
  "model_name": "my_model"
}
```

---

### `POST /publish`

Publish an approved artifact to DataHub.

**Request body**
```json
{
  "run_id": "f3a1b2c4-...",
  "approved": true
}
```

**Response**
```json
{
  "success": true,
  "model_urn": "urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.fct_orders,PROD)",
  "lineage": {
    "source": "urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.orders,PROD)",
    "generated_model": "urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.fct_orders,PROD)",
    "type": "TRANSFORMED"
  },
  "message": "Published successfully. Model 'fct_orders' is now discoverable in DataHub."
}
```

---

### `GET /health`

Health + configuration check.

```json
{
  "status": "ok",
  "demo_mode": true,
  "llm_provider": "mock",
  "version": "1.0.0"
}
```

---

## ⚙️ Configuration Reference

All settings can be set via environment variables or in your `.env` file.

| Variable | Default | Description |
|----------|---------|-------------|
| `DEMO_MODE` | `true` | Use fixture metadata and mock LLM. No external services needed |
| `LLM_PROVIDER` | `mock` | One of: `mock`, `anthropic`, `openai`, `gemini` |
| `ANTHROPIC_API_KEY` | *(empty)* | Anthropic API key (required when `LLM_PROVIDER=anthropic`) |
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key (required when `LLM_PROVIDER=openai`) |
| `GEMINI_API_KEY` | *(empty)* | Google AI API key (required when `LLM_PROVIDER=gemini`) |
| `DATAHUB_URL` | `http://localhost:8080` | DataHub REST API URL (used when `DEMO_MODE=false`) |
| `DATAHUB_TOKEN` | *(empty)* | DataHub personal access token |
| `MAX_REPAIR_ATTEMPTS` | `3` | Maximum LLM self-repair iterations |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS allowed origin for the frontend |
| `BACKEND_PORT` | `8000` | Docker only: host port for the backend |
| `FRONTEND_PORT` | `80` | Docker only: host port for the frontend |

---

## 🧪 Running Tests

```bash
cd backend
pytest -v
```

**Test suite: 52 tests across 6 files**

| File | Coverage |
|------|----------|
| `test_generation.py` | GenerationAgent JSON parsing, self-repair loop, `/generate` endpoint |
| `test_sql_validator.py` | AST symbol table contract enforcement |
| `test_semantic_validator.py` | Currency mixing, percentage aggregation, identifier arithmetic |
| `test_dbt_validator.py` | dbt YAML schema validation |
| `test_metadata_agent.py` | Metadata fetching, quality scoring, gap detection |
| `test_writeback.py` | DataHub lineage/tag/documentation payload structure |

---

## 🗺️ Roadmap

- [ ] **Streaming responses** — stream SQL token-by-token to the frontend
- [ ] **Multi-table joins** — reasoning agent support for cross-dataset foreign key joins
- [ ] **Live DataHub connection** — full `DEMO_MODE=false` production path with DataHub Cloud
- [ ] **dbt Cloud integration** — trigger dbt runs directly from the approval gate
- [ ] **Audit log** — persist generation runs and decisions to a database (SQLite/Postgres)
- [ ] **Custom dataset connectors** — pluggable metadata source adapters (Atlan, Alation, Collibra)

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for full contribution guidelines including:
- How to add a new LLM provider
- How to add a new demo dataset
- Commit message conventions
- Architecture principles

---

## 📄 License

MIT — see [LICENSE](./LICENSE) for details.

---

<div align="center">

Built with ❤️ using **FastAPI**, **React**, **dbt**, **sqlglot**, and **DataHub**

</div>
