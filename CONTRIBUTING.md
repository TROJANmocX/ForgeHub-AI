# Contributing to ForgeHub AI

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues
- Search existing issues before opening a new one.
- Include: Python/Node version, OS, steps to reproduce, and expected vs actual behaviour.

### Pull Requests
1. Fork the repository and create your branch from `develop`.
2. If adding a feature, add tests in `backend/tests/`.
3. If changing the API contract, update the TypeScript types in `frontend/src/types/index.ts`.
4. Ensure all tests pass: `cd backend && pytest`.
5. Ensure the frontend builds: `cd frontend && npm run build`.
6. Open a PR against `develop` (not `main`).

### Commit Message Format
Use [Conventional Commits](https://www.conventionalcommits.org/):
git clone https://github.com/TROJANmocX/ForgeHub-AI.git
cd ForgeHub-AI/
```
feat(generation): add streaming LLM response support
fix(validation): handle empty SQL on all-fail repair loop
docs(readme): add Docker deployment section
```

## Development Setup

See the [README](./README.md) for quick-start instructions.

## Code Style

### Python
- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use type annotations everywhere.
- Docstrings on all public classes and functions.

### TypeScript / React
- Use functional components with explicit prop types.
- Prefer explicit return types on exported functions.

## Architecture Principles

1. **The LLM is never trusted**. All generated SQL is mechanically validated against the DataHub symbol table via `sqlglot` AST analysis.
2. **Metadata is the source of truth**. No column or table may be referenced unless it exists in the DataHub-verified symbol table.
3. **Transparency first**. The reasoning plan is produced *before* any LLM call, giving users an inspectable, deterministic rationale.
4. **Self-repair is bounded**. The repair loop is capped at `MAX_REPAIR_ATTEMPTS` (default: 3) to prevent infinite loops.

## Adding a New LLM Provider

1. Create `backend/app/llm/myprovider.py` implementing `LLMProvider` base class.
2. Add a new `Literal` option to `llm_provider` in `backend/app/config.py`.
3. Wire it up in the `_get_llm_provider()` function in `backend/app/api/generation.py`.
4. Add `MYPROVIDER_API_KEY=` to `.env.example`.

## Adding a New Demo Dataset

1. Create a fixture JSON in `backend/app/datahub/fixtures/mydata.json` (follow the schema from `orders.json`).
2. Register it in `FIXTURE_REGISTRY` in `backend/app/datahub/client.py`.
3. Add pre-baked SQL/schema/readme artifacts in `backend/app/llm/mock.py`.
4. If the dataset has special reasoning logic, extend `backend/app/agents/reasoning_agent.py`.
