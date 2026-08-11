# FORGEHUB AI

## Metadata-Aware AI Data Engineering Agent

### Product Definition

Build **ForgeHub AI**, an intelligent, metadata-aware AI data engineering platform that connects to **DataHub**, reads verified dataset metadata, performs structured reasoning, identifies metadata quality gaps, generates production-ready **dbt models**, tests, and documentation, validates every generated artifact against strict schema and semantic contracts, and publishes the resulting models, documentation, tags, and lineage back into DataHub.

ForgeHub AI is **not** a generic AI SQL generator.

Its fundamental rule is:

> **DataHub metadata is the source of truth.**

The AI must never blindly invent tables, columns, relationships, business definitions, units, currencies, identifiers, or governance information.

The system should behave like a senior data engineer operating under strict governance constraints.

---

# 1. CORE PROBLEM

Traditional AI SQL generators can produce syntactically valid SQL that is completely wrong.

Examples:

* Referencing columns that don't exist.
* Inventing table names.
* Joining datasets using incorrect keys.
* Treating USD and EUR as interchangeable.
* Summing percentages or rates.
* Assuming undocumented business definitions.
* Ignoring PII or governance metadata.
* Creating models without understanding the actual dataset grain.
* Producing documentation that contradicts the source catalog.

ForgeHub AI solves this by putting a **metadata contract between the AI and the database**.

The LLM is never given unrestricted freedom.

Instead:

```text
DataHub Metadata
       ↓
Verified Metadata Contract
       ↓
Symbol Table + Semantic Types
       ↓
Structured Reasoning
       ↓
SQL/dbt Generation
       ↓
AST Validation
       ↓
Semantic Validation
       ↓
Artifact Validation
       ↓
DataHub Write-back
```

---

# 2. VISION

Create an AI data engineering agent capable of turning trusted catalog metadata into production-ready dbt artifacts while making hallucinated data references structurally difficult or impossible.

The system should demonstrate five major architectural principles.

---

## PRINCIPLE 1 — DataHub Glossary as a Semantic Type System

SQL syntax alone is insufficient to determine whether a query is correct.

The system must use DataHub glossary terms, descriptions, tags, and metadata to understand semantic meaning.

For example:

```text
revenue_usd → Currency(USD)
revenue_eur → Currency(EUR)
discount_rate → Percentage
order_quantity → Quantity
customer_id → Identifier
```

The validation layer should detect logically invalid operations such as:

```sql
SUM(revenue_usd + revenue_eur)
```

or:

```sql
SUM(discount_rate)
```

when the metadata indicates that such operations are semantically invalid.

The system should distinguish between:

```text
SQL-valid
```

and:

```text
Business-valid
```

---

# 3. PRINCIPLE 2 — MAKE HALLUCINATIONS STRUCTURALLY UNREPRESENTABLE

Before generation, construct a verified symbol table from DataHub.

Example:

```json
{
  "retail.orders": {
    "columns": {
      "order_id": "identifier",
      "customer_id": "identifier",
      "quantity": "quantity",
      "unit_price": "currency"
    }
  }
}
```

The SQL generation agent must only be allowed to reference symbols contained within this verified contract.

If the model generates:

```sql
SELECT customer_name
FROM retail.orders
```

but `customer_name` does not exist in the DataHub metadata:

```text
VALIDATION FAILED
UNKNOWN_COLUMN: customer_name
```

Likewise:

```sql
FROM retail.magic_orders
```

must result in:

```text
VALIDATION FAILED
UNKNOWN_TABLE: retail.magic_orders
```

Do not solve hallucination by simply asking the LLM to "try again."

The architecture must reject invalid references mechanically.

---

# 4. PRINCIPLE 3 — DATAHUB AS LONG-TERM AGENT MEMORY

ForgeHub AI should use DataHub as more than a metadata source.

The platform should write useful knowledge back into DataHub.

Examples:

* Generated model documentation.
* AI-generated tags.
* Data quality observations.
* Semantic classifications.
* Model lineage.
* Assumption records.
* Human feedback.
* Approved transformations.

This creates a feedback loop:

```text
Human
  ↓
ForgeHub AI
  ↓
Generated Artifact
  ↓
Validation
  ↓
Human Approval
  ↓
DataHub
  ↓
Better Metadata
  ↓
Better Future Generations
```

---

# 5. PRINCIPLE 4 — PROVENANCE RECEIPTS

Every important generated decision should have provenance.

The system should be able to answer:

> "Why did the AI generate this transformation?"

Example:

```json
{
  "decision": "Calculate order_value",
  "expression": "quantity * unit_price",
  "evidence": [
    {
      "asset": "retail.orders.quantity",
      "metadata": "Quantity"
    },
    {
      "asset": "retail.orders.unit_price",
      "metadata": "Currency"
    }
  ],
  "confidence": 0.97
}
```

Generated artifacts should therefore have explainability metadata.

The system should maintain a relationship between:

```text
Generated SQL
      ↓
Transformation
      ↓
DataHub Metadata
      ↓
Evidence
```

---

# 6. PRINCIPLE 5 — EMPIRICAL ENSEMBLE VERIFICATION

Use multiple generation or validation strategies when appropriate.

For example:

```text
Strategy A → SQL proposal
Strategy B → SQL proposal
Strategy C → SQL proposal
             ↓
        Compare results
             ↓
      Detect disagreement
             ↓
     Investigate ambiguity
```

If multiple strategies disagree because metadata is incomplete or ambiguous, the system should flag the dataset instead of pretending to know the answer.

Example:

```text
METADATA AMBIGUITY DETECTED

Field: unit_price

Possible interpretations:
1. USD
2. Local currency

Confidence: LOW

Generation blocked until metadata is clarified.
```

---

# 7. AGENT WORKFLOW

ForgeHub AI should implement the following workflow.

## STEP 1 — Dataset Discovery

Retrieve dataset information from DataHub.

Retrieve:

* Dataset name.
* Platform.
* Environment.
* Schema.
* Columns.
* Data types.
* Column descriptions.
* Dataset description.
* Owners.
* Domains.
* Glossary terms.
* Tags.
* PII classification.
* Primary keys.
* Foreign keys.
* Upstream lineage.
* Downstream lineage.
* Dataset properties.

Normalize all metadata into strongly typed Pydantic models.

---

# 8. METADATA NORMALIZATION

Create models such as:

```python
class ColumnMetadata(BaseModel):
    name: str
    data_type: str
    description: str | None
    glossary_terms: list[str]
    tags: list[str]
    nullable: bool | None
    is_primary_key: bool
    is_foreign_key: bool
```

```python
class DatasetMetadata(BaseModel):
    urn: str
    name: str
    platform: str
    environment: str
    description: str | None
    columns: list[ColumnMetadata]
    owners: list[str]
    domains: list[str]
    glossary_terms: list[str]
    tags: list[str]
    upstream_datasets: list[str]
    downstream_datasets: list[str]
```

Do not allow untyped dictionaries to become the primary internal representation.

Use explicit contracts.

---

# 9. METADATA QUALITY ENGINE

Create a metadata quality score from:

```text
0 → 100
```

Evaluate:

* Dataset description completeness.
* Column description coverage.
* Glossary term coverage.
* Ownership metadata.
* Domain assignment.
* Primary key metadata.
* Foreign key metadata.
* Lineage availability.
* Governance tags.
* PII classification.
* Semantic unit/currency information.

Example:

```text
Metadata Quality Score: 72/100
```

Breakdown:

```text
Schema completeness       95%
Descriptions              70%
Glossary coverage         55%
Lineage                   100%
Governance                80%
Semantic metadata         40%
```

The UI must clearly show why the score exists.

Do not produce a meaningless AI-generated number.

---

# 10. METADATA GAP DETECTOR

Detect explicit metadata deficiencies.

Examples:

```text
UNDEFINED_CURRENCY
MISSING_COLUMN_DESCRIPTION
MISSING_PRIMARY_KEY_SCOPE
MISSING_FOREIGN_KEY
MISSING_DOMAIN
MISSING_GLOSSARY_TERM
MISSING_LINEAGE
MISSING_OWNER
AMBIGUOUS_SEMANTIC_TYPE
MISSING_PII_CLASSIFICATION
```

Each gap should contain:

```json
{
  "type": "UNDEFINED_CURRENCY",
  "asset": "retail.orders.unit_price",
  "severity": "high",
  "reason": "Currency unit is not defined in metadata",
  "generation_impact": "Cannot safely perform cross-currency aggregation"
}
```

The system should distinguish:

```text
Informational
Warning
Blocking
```

gaps.

---

# 11. STRUCTURED REASONING AGENT

Before generating SQL, create a structured reasoning object.

Do NOT rely on free-form hidden reasoning.

Produce an inspectable plan containing:

```json
{
  "model_name": "fct_orders",
  "grain": "one row per order",
  "source_tables": [
    "retail.orders"
  ],
  "transformations": [
    {
      "name": "order_value",
      "expression": "quantity * unit_price",
      "reason": "Quantity multiplied by unit price"
    }
  ],
  "tests": [
    "order_id must be unique",
    "order_id must not be null"
  ],
  "assumptions": [],
  "metadata_gaps": [],
  "explainability": []
}
```

Each major decision should contain:

```text
Decision
Evidence
Confidence
```

Never expose private chain-of-thought.

Only expose concise structured reasoning and evidence.

---

# 12. LLM PROVIDER ABSTRACTION

Create a provider-independent LLM interface.

Support:

```text
Anthropic Claude
OpenAI
Google Gemini
Mock Provider
```

Architecture:

```python
class LLMProvider(ABC):

    def generate(self, prompt: str) -> str:
        ...
```

Implement:

```text
ClaudeProvider
OpenAIProvider
GeminiProvider
MockProvider
```

The rest of the application must not depend directly on a specific LLM provider.

---

# 13. DEMO MODE

Implement a deterministic demo mode.

Configuration:

```env
DEMO_MODE=true
LLM_PROVIDER=mock
```

Demo mode must require:

* No DataHub server.
* No API keys.
* No external services.

Provide predefined metadata snapshots for:

```text
orders
customers
revenue
```

The entire pipeline must function locally.

This is critical for demos, testing, judging, and development.

---

# 14. SQL GENERATION

Generate production-ready dbt models.

Each generation should produce:

```text
model.sql
schema.yml
README.md
```

SQL should use:

* CTEs.
* Explicit column selection.
* Clear aliases.
* Safe transformations.
* dbt-compatible syntax.
* No `SELECT *` unless explicitly justified.

Example:

```sql
WITH orders AS (

    SELECT
        order_id,
        customer_id,
        quantity,
        unit_price
    FROM {{ source('retail', 'orders') }}

),

final AS (

    SELECT
        order_id,
        customer_id,
        quantity,
        unit_price,
        quantity * unit_price AS order_value
    FROM orders

)

SELECT *
FROM final
```

---

# 15. SQL AST VALIDATION

Use `sqlglot`.

Parse every generated SQL statement into an AST.

Validate:

### Syntax

```text
Is valid SQL?
```

### Tables

```text
Does every referenced table exist in DataHub?
```

### Columns

```text
Does every referenced column exist in its source?
```

### Aliases

```text
Are aliases correctly scoped?
```

### Functions

```text
Are transformations allowed?
```

### Semantic types

```text
Are mathematical operations semantically valid?
```

### Grain

```text
Does the transformation preserve or intentionally change model grain?
```

---

# 16. SELF-REPAIR LOOP

Invalid generated SQL must enter a controlled repair loop.

Architecture:

```text
Generate
   ↓
Validate
   ↓
Invalid?
   ├── No → Continue
   │
   └── Yes
        ↓
      Error Report
        ↓
      Repair
        ↓
      Validate Again
```

Set a maximum retry count.

Example:

```text
MAX_REPAIR_ATTEMPTS=3
```

Never allow infinite LLM retry loops.

If validation still fails:

```text
GENERATION_FAILED
```

with a clear explanation.

---

# 17. DBT YAML VALIDATION

Validate generated `schema.yml`.

Ensure:

* Models exist.
* Columns exist.
* Tests reference valid columns.
* Descriptions are present.
* dbt structure is valid.
* No hallucinated columns exist.

Automatically support tests such as:

```yaml
tests:
  - unique
  - not_null
```

Where metadata supports them.

---

# 18. AUTOMATIC TEST GENERATION

Generate tests based on metadata.

Examples:

Primary key:

```yaml
- unique
- not_null
```

Foreign key:

```yaml
relationships
```

Business constraints:

```text
accepted_values
```

when metadata provides the required information.

Do not invent constraints that DataHub cannot support.

---

# 19. DOCUMENTATION GENERATION

Generate production-quality documentation.

README should contain:

```text
Model Overview
Source Datasets
Model Grain
Columns
Transformations
Tests
Metadata Gaps
Assumptions
Lineage
Governance
Generation Provenance
```

Documentation must distinguish between:

```text
Verified metadata
```

and:

```text
AI inference
```

---

# 20. DATAHUB WRITE-BACK

After successful validation and optional human approval, publish artifacts back to DataHub.

Support:

* Dataset entities.
* AI-generated tags.
* Documentation.
* README/aspect updates.
* Upstream lineage.
* Downstream lineage.
* Model metadata.

Example lineage:

```text
retail.orders
      ↓
forgehub.fct_orders
```

The generated model should become discoverable in DataHub.

---

# 21. HUMAN APPROVAL GATE

Never automatically publish uncertain artifacts.

Use statuses:

```text
DRAFT
VALIDATED
REQUIRES_REVIEW
APPROVED
PUBLISHED
FAILED
```

Example:

```text
Metadata Quality: 62/100

Blocking Gaps:
• Currency undefined
• Foreign key undocumented

Status:
REQUIRES_REVIEW
```

The user can review the gaps before publishing.

---

# 22. FRONTEND

Build a modern React + Vite dashboard.

Use:

```text
React
TypeScript
Tailwind CSS
```

Recommended interface:

```text
┌───────────────────────────────────────────────┐
│ ForgeHub AI                         DataHub ● │
├───────────────┬───────────────────────────────┤
│               │                               │
│ Datasets      │ Dataset Overview              │
│               │                               │
│ Orders        │ retail.orders                 │
│ Customers     │                               │
│ Revenue       │ Quality Score   82/100        │
│               │                               │
│               │ Metadata Gaps                 │
│               │ ⚠ Currency undefined          │
│               │ ⚠ Country code undocumented   │
│               │                               │
│               │ [Generate dbt Model]          │
│               │                               │
└───────────────┴───────────────────────────────┘
```

---

# 23. DASHBOARD SECTIONS

Create components for:

### Dataset Context

Show:

* Dataset name.
* Platform.
* Owner.
* Domain.
* Description.
* Tags.
* Glossary terms.

### Metadata Quality

Display:

```text
Overall Score
Schema
Documentation
Governance
Lineage
Semantic Metadata
```

### Metadata Gaps

Display:

```text
Critical
Warning
Informational
```

### Reasoning

Show the structured reasoning plan.

Display:

```text
Decision
Evidence
Confidence
```

Do not display hidden chain-of-thought.

### Generated Artifacts

Tabs:

```text
SQL
schema.yml
README
```

Include syntax highlighting.

### Validation

Display:

```text
SQL Syntax       PASS
Table References PASS
Column References PASS
Semantic Checks  PASS
dbt Schema       PASS
Tests             PASS
```

### Lineage

Visualize:

```text
Source → Generated Model
```

### Publish

Provide:

```text
Review
Approve
Publish to DataHub
```

---

# 24. BACKEND API

Implement FastAPI endpoints:

```text
GET  /health
GET  /datasets
GET  /datasets/{dataset_id}
POST /generate
POST /validate
POST /publish
GET  /runs/{run_id}
```

Use Pydantic request/response models.

Never expose internal implementation details through loosely structured JSON.

---

# 25. PROJECT STRUCTURE

Use:

```text
forgehub-ai/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   ├── datasets.py
│   │   │   ├── generation.py
│   │   │   ├── validation.py
│   │   │   └── publish.py
│   │   │
│   │   ├── agents/
│   │   │   ├── metadata_agent.py
│   │   │   ├── quality_agent.py
│   │   │   ├── reasoning_agent.py
│   │   │   └── generation_agent.py
│   │   │
│   │   ├── datahub/
│   │   │   ├── client.py
│   │   │   ├── metadata.py
│   │   │   └── writeback.py
│   │   │
│   │   ├── llm/
│   │   │   ├── base.py
│   │   │   ├── claude.py
│   │   │   ├── openai.py
│   │   │   ├── gemini.py
│   │   │   └── mock.py
│   │   │
│   │   ├── validation/
│   │   │   ├── sql_validator.py
│   │   │   ├── semantic_validator.py
│   │   │   └── dbt_validator.py
│   │   │
│   │   └── models/
│   │       ├── metadata.py
│   │       ├── reasoning.py
│   │       ├── generation.py
│   │       └── artifacts.py
│   │
│   ├── tests/
│   │   ├── test_metadata_agent.py
│   │   ├── test_quality.py
│   │   ├── test_sql_validator.py
│   │   ├── test_semantic_validator.py
│   │   └── test_writeback.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── types/
│   │   └── App.tsx
│   └── package.json
│
├── examples/
│   ├── orders/
│   ├── customers/
│   └── revenue/
│
├── prompts/
├── scripts/
├── .env.example
├── README.md
└── LICENSE
```

---

# 26. PRE-BUILT EXAMPLES

Create three deterministic examples.

## ORDERS

Dataset:

```text
retail.orders
```

Generate:

```text
fct_orders
```

Transformation:

```text
order_value = quantity * unit_price
```

Tests:

```text
order_id unique
order_id not null
```

Intentionally include:

```text
Undefined Currency
```

as a metadata gap.

The system should identify the gap rather than silently assume USD.

---

# 27. CUSTOMERS

Dataset:

```text
retail.customers
```

Generate:

```text
dim_customers
```

Transform:

```text
full_name
clean_email
```

Preserve:

```text
country_code
```

without inventing its semantic meaning if metadata does not define it.

---

# 28. REVENUE

Create:

```text
monthly_revenue
```

Perform monthly financial cohort aggregation.

Include promotional discounts.

Validate:

```text
revenue
discount
net_revenue
```

semantically.

The system must prevent invalid financial aggregation when currency metadata is ambiguous.

---

# 29. TESTING

The project must have meaningful automated tests.

Test:

### Metadata

```text
Schema normalization
Quality score
Metadata gap detection
```

### SQL

```text
Valid SQL
Hallucinated columns
Hallucinated tables
Invalid aliases
```

### Semantic Validation

```text
Currency mismatch
Invalid percentage aggregation
Identifier misuse
```

### dbt

```text
Invalid schema.yml
Unknown columns
Missing model references
```

### Writeback

```text
DataHub payload generation
Lineage edges
Tags
Documentation
```

---

# 30. SECURITY AND SAFETY

Never expose:

```text
API keys
DataHub tokens
Secrets
```

in frontend responses.

Use environment variables.

Sanitize generated content before write-back.

Do not execute generated SQL automatically against production databases.

Generation and publishing must remain separate operations.

---

# 31. CONFIGURATION

Provide:

```env
DEMO_MODE=true

DATAHUB_URL=http://localhost:8080
DATAHUB_TOKEN=

LLM_PROVIDER=mock

ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=

MAX_REPAIR_ATTEMPTS=3
```

---

# 32. DEVELOPMENT REQUIREMENTS

The application must run without Docker.

Backend:

```text
Python 3.9+
FastAPI
Pydantic
sqlglot
pytest
```

Frontend:

```text
Node 18+/22+
React
TypeScript
Vite
Tailwind
```

Provide complete installation instructions.

---

# 33. DEMO EXPERIENCE

The demo should tell a clear story.

User selects:

```text
retail.orders
```

ForgeHub AI displays:

```text
Metadata Quality: 82/100

Detected Issues:
⚠ Currency undefined
```

User clicks:

```text
Generate Model
```

The system displays:

```text
Reasoning Plan
       ↓
Generated SQL
       ↓
Validation
       ↓
dbt Tests
       ↓
Documentation
```

Then:

```text
Validation Passed

✓ SQL syntax
✓ Tables
✓ Columns
✓ Semantic rules
✓ dbt schema
✓ Tests
```

Finally:

```text
Publish to DataHub
```

and displays:

```text
Published Successfully

retail.orders
      ↓
forgehub.fct_orders
```

---

# 34. FAILURE DEMO

The project must also demonstrate that it can reject bad AI output.

Provide an intentionally broken generation such as:

```sql
SELECT
    customer_name,
    fake_revenue
FROM retail.orders
```

Validator output:

```text
GENERATION REJECTED

UNKNOWN_COLUMN:
customer_name

UNKNOWN_COLUMN:
fake_revenue
```

This is a core demonstration feature.

The audience should immediately understand:

> The AI isn't trusted. The metadata contract is.

---

# 35. ENGINEERING PRINCIPLES

Follow these priorities:

```text
Correctness
    ↓
Traceability
    ↓
Validation
    ↓
Security
    ↓
Clarity
    ↓
Performance
    ↓
Polish
```

Do not over-engineer.

Prefer simple, testable modules.

Avoid unnecessary microservices.

Keep the initial implementation as a modular monolith.

---

# 36. FINAL PRODUCT STANDARD

ForgeHub AI should feel like a real internal enterprise data platform rather than an AI demo.

The final product must demonstrate:

1. Real DataHub metadata ingestion.
2. Deterministic metadata normalization.
3. Metadata quality scoring.
4. Explicit metadata gap detection.
5. Structured reasoning.
6. Provider-independent LLM generation.
7. Strict symbol-table enforcement.
8. SQL AST validation.
9. Semantic validation.
10. dbt model generation.
11. dbt test generation.
12. Documentation generation.
13. Self-repair.
14. Human approval.
15. DataHub write-back.
16. Model lineage.
17. Provenance.
18. Deterministic demo mode.
19. Automated tests.
20. A polished React dashboard.

The most important product principle is:

> **ForgeHub AI does not ask the LLM what the data looks like. It asks DataHub what the data is, then forces the LLM to operate inside those boundaries.**

Build the system around that principle.

Do not reduce ForgeHub AI into a chatbot that happens to generate SQL.

It is an **AI data engineering agent governed by metadata contracts**.
