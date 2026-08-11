# ForgeHub-AI

<div align="center">

# ForgeHub AI

### the AI data engineering agent that actually understood the assignment

[![CI](https://github.com/TROJANmocX/ForgeHub-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/TROJANmocX/ForgeHub-AI/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-20%20|%2022-green?logo=node.js&logoColor=white)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

**ForgeHub AI** hooks into **DataHub**, reads your verified dataset metadata, enforces symbol table contracts, spits out production-ready **dbt models**, tests, and docs — then writes verified lineage straight back to DataHub. The LLM is literally never trusted to make up tables or columns. Hallucinated references get cooked at the AST layer. No cap.

> zero external dependencies in Demo Mode — runs fully offline with mock LLM and fixture metadata. That's based.

[Quick Start](#quick-start) · [Demo Tour](#dashboard-tour--demo-flow) · [Architecture](#architecture) · [Docker](#docker-deployment) · [LLM Providers](#llm-providers) · [API Docs](#api-reference) · [Contributing](./CONTRIBUTING.md)

</div>

---

## fr fr, what is this

okay so picture this: your data team is cooked. everyone's vibing with AI tools but every time you ask a model to write SQL, it just starts hallucinating columns that don't exist. major L. 

ForgeHub AI said "not on my watch" and built an entire mechanical validation layer that straight up rejects anything the LLM makes up. the model has no rizz without your metadata. that's the whole bit.

it reads your DataHub catalog, understands your schema, builds a reasoning plan *before* even touching the LLM, and then validates everything with AST-level SQL parsing. if it hallucinates, we catch it. if it tries again and still fails, we catch it again. the self-repair loop eats for free (max 3 attempts tho, we're not cooked).

---

## the features are lowkey insane

| Feature | the tea |
|---------|---------|
| Symbol Table Contract | generation is mechanically constrained to symbols in DataHub. hallucinated columns get yeeted by `sqlglot` AST validation. no cap. |
| Semantic Type Safety | prevents illegal ops: mixed-currency addition, summing percentages, arithmetic on identifiers. it's giving guardrails. |
| Metadata Quality Engine | scores datasets 0-100 with per-gap breakdowns (Blocking / Warning / Informational). actually goated. |
| Inspectable Reasoning | produces a pre-generation plan with decision evidence and confidence scores *before* any LLM call. full transparency era. |
| Self-Repair Loop | automatically feeds AST/YAML validation errors back into the LLM (max 3 attempts). it ate and left no crumbs. |
| DataHub Write-Back | writes model docs, AI tags, and upstream lineage back to DataHub. slay. |
| Demo Mode | fully functional offline with zero API keys. we stay winning. |
| Failure Demo | built-in "Break It" feature shows real-time contract rejection of hallucinated SQL. the villain arc we needed. |

---

## architecture (she's built different)

```
DataHub Metadata / Fixtures
       |
       v
+-----------------------------+
|     Metadata Agent          |  -> fetches + normalises DataHub metadata
|     + Symbol Table Builder  |  -> builds the verified symbol contract
+-----------------------------+
       |
       v
+-----------------------------+
|     Quality Agent           |  -> scores 0-100, detects blocking gaps
+-----------------------------+
       |
       v
+-----------------------------+
|     Reasoning Agent         |  -> deterministic plan: grain, transforms, tests
+-----------------------------+
       |
       v
+-----------------------------+
|     Generation Agent        |  -> calls LLM via provider abstraction
|     + Self-Repair Loop      |  -> re-prompts with errors (max 3 attempts)
+-----------------------------+
       | (SQL + schema.yml + README.md)
       v
+-----------------------------------------------------+
|                  Validation Layer                   |
|  +-- AST Validator (sqlglot) -- symbol table check  |
|  +-- Semantic Type Validator -- currency/pct/id     |
|  +-- dbt YAML Validator -- schema contract          |
+-----------------------------------------------------+
       |
       v
+-----------------------------+
|  Human Approval & Governance|  <- you have the final say bestie
+-----------------------------+
       |
       v
+-----------------------------+
|  DataHub Write-Back         |  -> lineage, tags, documentation
+-----------------------------+
```

### LLM Provider tier list (they're all valid)

```
LLMProvider (base class, no cap the real one)
+-- MockProvider        -- deterministic, zero API keys, demo mode (S tier for devs)
+-- ClaudeProvider      -- Anthropic claude-3-5-sonnet (S tier, bussin)
+-- OpenAIProvider      -- OpenAI gpt-4o (A tier, solid)
+-- GeminiProvider      -- Google gemini-1.5-pro (A tier, understood the assignment)
```

---

## Quick Start

### before you do anything, check your setup

| Tool | Minimum Version | vibe check |
|------|----------------|------------|
| Python | 3.11+ (3.12 recommended) | serve |
| Node.js | 18+ (20 or 22 recommended) | serve |
| npm | 8+ | mid but necessary |

### 1. clone it (obviously)

```bash
git clone https://github.com/TROJANmocX/ForgeHub-AI.git
cd ForgeHub-AI
```

### 2. set up your env (lowkey important)

```bash
cp .env.example .env
```

the default `.env` enables Demo Mode (`DEMO_MODE=true`, `LLM_PROVIDER=mock`) — no external dependencies required. run it in your room at 3am, we don't gatekeep.

### 3. backend (the real one)

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

FastAPI server: `http://localhost:8000`  
interactive API docs (actually kinda fire): `http://localhost:8000/docs`

### 4. frontend (she's pretty)

```bash
cd frontend
npm install
npm run dev
```

dashboard: `http://localhost:5173`

---

## Docker Deployment

run the entire stack with literally one command. no python, no node, just vibes.

```bash
# copy and configure env
cp .env.example .env

# build and start
docker compose up --build

# dashboard  ->  http://localhost:80
# API        ->  http://localhost:8000
# API docs   ->  http://localhost:8000/docs
```

### what's cooking in docker compose

| Service | Image | Port | verdict |
|---------|-------|------|---------|
| `backend` | Python 3.12 slim + FastAPI | `8000` | it's giving efficiency |
| `frontend` | Node 22 build + Nginx 1.27 | `80` | slay |

### custom ports if you're that person

```bash
BACKEND_PORT=9000 FRONTEND_PORT=3000 docker compose up
```

### tear it down

```bash
docker compose down        # stop
docker compose down -v     # stop + remove volumes (nuclear option)
```

---

## Dashboard Tour -- Demo Flow

no cap this is actually fun to watch:

1. **Select Dataset**: click `retail.orders` in the left catalog sidebar.
2. **Inspect Quality and Gaps**: observe quality score **82/100** and blocking gap: `UNDEFINED_CURRENCY -- unit_price currency unit not specified`. the metadata is cooked.
3. **Generate Model**: click **Generate dbt Model**. watch the structured reasoning plan materialise, followed by `model.sql`, `schema.yml`, and `README.md`. it ate.
4. **Validation Checklist**: green checkmarks for SQL Syntax, Table References, Column References, Semantic Safety, dbt Schema, and Tests. we ate and left no crumbs.
5. **Break It**: click **Failure Demo (Break It)** to watch the AST contract absolutely cook hallucinated columns (`customer_name`, `fake_revenue`). villain arc, we love to see it.
6. **Publish to DataHub**: click **Approve and Publish to DataHub**. lineage graph writes back (`retail.orders -> forgehub.fct_orders`). the pipeline understood the assignment.

### Demo Datasets (they're all bussing different)

| Dataset | Model Generated | Quality Score | the drama |
|---------|----------------|---------------|-----------|
| `retail.orders` | `fct_orders` | 82/100 | `UNDEFINED_CURRENCY` on `unit_price` (blocking, major L) |
| `retail.customers` | `dim_customers` | 75.5/100 | `AMBIGUOUS_SEMANTIC_TYPE` on `country_code`, `MISSING_PII_CLASSIFICATION` on `email` (messy) |
| `retail.revenue` | `monthly_revenue` | 68/100 | 2x `UNDEFINED_CURRENCY` on `gross_revenue` and `discount_amount` (she's not okay) |

---

## LLM Providers

switch providers by setting env vars. zero code changes. that's the era we're in.

### Mock (Default -- free as in free ninety-nine)

```env
DEMO_MODE=true
LLM_PROVIDER=mock
```

pre-baked deterministic dbt artifacts. fully offline. we don't gatekeep.

### Anthropic Claude (S tier no cap)

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
DEMO_MODE=false
```

uses `claude-3-5-sonnet-20241022` by default. she's built different.

```bash
pip install anthropic
```

### OpenAI GPT-4o (A tier, solid)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
DEMO_MODE=false
```

```bash
pip install openai
```

### Google Gemini (A tier, understood the assignment)

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
DEMO_MODE=false
```

```bash
pip install google-generativeai
```

> when `DEMO_MODE=true`, mock provider always runs regardless of `LLM_PROVIDER`. we don't negotiate.

---

## Repository Structure (the full lore)

```
ForgeHub-AI/
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml              # GitHub Actions: test + build + Docker (she works hard)
|
+-- backend/
|   +-- app/
|   |   +-- agents/             # the agents are that girl
|   |   |   +-- generation_agent.py
|   |   |   +-- metadata_agent.py
|   |   |   +-- quality_agent.py
|   |   |   +-- reasoning_agent.py
|   |   +-- api/                # FastAPI routers
|   |   |   +-- datasets.py     # GET /datasets
|   |   |   +-- generation.py   # POST /generate
|   |   |   +-- publish.py      # POST /publish
|   |   |   +-- validation.py   # POST /validate
|   |   +-- datahub/            # DataHub client + fixtures + write-back
|   |   +-- llm/                # LLM provider abstraction (based)
|   |   |   +-- base.py
|   |   |   +-- claude.py
|   |   |   +-- gemini.py
|   |   |   +-- mock.py
|   |   |   +-- openai.py
|   |   +-- models/             # Pydantic models (strict, no cap)
|   |   +-- validation/         # AST + Semantic + dbt YAML validators
|   |   +-- config.py
|   |   +-- main.py
|   +-- tests/                  # 52 tests -- we stay testing
|   +-- Dockerfile
|   +-- requirements.txt
|
+-- frontend/
|   +-- src/
|   |   +-- api/client.ts       # REST API client
|   |   +-- components/         # 13 components -- she's stacked
|   |   +-- types/index.ts      # TypeScript interfaces (typed up, no cap)
|   |   +-- App.tsx
|   |   +-- index.css
|   +-- Dockerfile
|   +-- nginx.conf              # production Nginx (efficient queen)
|   +-- package.json
|   +-- vite.config.ts
|
+-- docker-compose.yml          # one command to rule them all
+-- .env.example                # copy to .env, fill in your keys
+-- .gitignore
+-- CONTRIBUTING.md
+-- LICENSE
+-- README.md                   # you are here bestie
```

---

## API Reference

Base URL: `http://localhost:8000`  
interactive docs (actually fire): `http://localhost:8000/docs`

### GET /datasets

list all available datasets. straightforward, no drama.

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

### GET /datasets/{dataset_id}

full metadata and quality report. the full lore on your dataset.

**Response** (abbreviated)
```json
{
  "id": "orders",
  "name": "retail.orders",
  "quality": {
    "overall_score": 82.0,
    "gaps": [
      {
        "type": "UNDEFINED_CURRENCY",
        "asset": "retail.orders.unit_price",
        "severity": "blocking",
        "reason": "Column 'unit_price' appears to be a monetary value but has no currency unit defined.",
        "generation_impact": "Cannot safely perform financial aggregation. She's cooked."
      }
    ]
  }
}
```

---

### POST /generate

the main event. runs the full ForgeHub AI pipeline. this is where the magic happens fr.

**Request body**
```json
{
  "dataset_id": "orders",
  "model_name": null,
  "broken_mode": false
}
```

| Field | Type | the deal |
|-------|------|---------|
| `dataset_id` | string | which dataset to generate a model for |
| `model_name` | string? | override the auto-inferred dbt model name |
| `broken_mode` | boolean | set `true` to watch the hallucination fail in real time (villain mode) |

**Status values -- the vibe check**

| Status | what it means |
|--------|---------------|
| `VALIDATED` | all checks pass, no blocking gaps. she ate. |
| `REQUIRES_REVIEW` | checks pass but blocking metadata gaps exist. needs attention bestie. |
| `FAILED` | AST, semantic, or schema validation failed. cooked. |

---

### POST /validate

validate arbitrary SQL and schema YAML against a dataset's symbol table. useful for checking your own work before committing.

---

### POST /publish

publish an approved artifact to DataHub. write-back goes brrr.

**Response**
```json
{
  "success": true,
  "model_urn": "urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.fct_orders,PROD)",
  "message": "Published successfully. Model 'fct_orders' is now discoverable in DataHub."
}
```

---

### GET /health

sanity check. `{"status": "ok"}` means we're good.

---

## Configuration Reference

| Variable | Default | the vibe |
|----------|---------|---------|
| `DEMO_MODE` | `true` | use fixture metadata + mock LLM. zero external services. |
| `LLM_PROVIDER` | `mock` | one of: `mock`, `anthropic`, `openai`, `gemini` |
| `ANTHROPIC_API_KEY` | empty | required when `LLM_PROVIDER=anthropic` |
| `OPENAI_API_KEY` | empty | required when `LLM_PROVIDER=openai` |
| `GEMINI_API_KEY` | empty | required when `LLM_PROVIDER=gemini` |
| `DATAHUB_URL` | `http://localhost:8080` | DataHub REST API URL (when `DEMO_MODE=false`) |
| `DATAHUB_TOKEN` | empty | DataHub personal access token |
| `MAX_REPAIR_ATTEMPTS` | `3` | maximum LLM self-repair iterations. we don't let it cook forever. |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS allowed origin |
| `BACKEND_PORT` | `8000` | Docker host port for backend |
| `FRONTEND_PORT` | `80` | Docker host port for frontend |

---

## Running Tests

```bash
cd backend
pytest -v
```

**52 tests, 0 failures. we ate.**

| File | What gets tested |
|------|---------|
| `test_generation.py` | GenerationAgent JSON parsing, self-repair loop, /generate endpoint |
| `test_sql_validator.py` | AST symbol table contract enforcement -- the main character |
| `test_semantic_validator.py` | currency mixing, percentage aggregation, identifier arithmetic |
| `test_dbt_validator.py` | dbt YAML schema validation |
| `test_metadata_agent.py` | metadata fetching, quality scoring, gap detection |
| `test_writeback.py` | DataHub lineage/tag/documentation payload structure |

---

## Roadmap (the pipeline, no pun intended)

- [ ] streaming responses -- stream SQL token-by-token to the frontend (low latency era)
- [ ] multi-table joins -- reasoning agent support for cross-dataset foreign key joins
- [ ] live DataHub connection -- full `DEMO_MODE=false` production path with DataHub Cloud
- [ ] dbt Cloud integration -- trigger dbt runs directly from the approval gate
- [ ] audit log -- persist generation runs to a database (SQLite/Postgres)
- [ ] custom dataset connectors -- pluggable metadata source adapters (Atlan, Alation, Collibra)

---

## Architecture Principles (these hit different)

1. **The LLM is never trusted.** All generated SQL is mechanically validated against the DataHub symbol table via `sqlglot` AST analysis. no cap, no exceptions.
2. **Metadata is the source of truth.** No column or table may be referenced unless it exists in the DataHub-verified symbol table. period.
3. **Transparency first.** The reasoning plan is produced *before* any LLM call. the lore is fully accessible.
4. **Self-repair is bounded.** The repair loop is capped at `MAX_REPAIR_ATTEMPTS` (default 3). we let it cook but not forever.

---

## Contributing

see [CONTRIBUTING.md](./CONTRIBUTING.md) for the full rundown including how to add new LLM providers, new demo datasets, commit conventions, and the architecture principles that keep this project from going cooked.

fr any PR that adds tests gets merged faster. that's just the truth.

---

## License

MIT -- see [LICENSE](./LICENSE). do what you want with it bestie, just keep the license.

---

<div align="center">

built with FastAPI, React, dbt, sqlglot, and DataHub

the metadata understood the assignment

</div>
