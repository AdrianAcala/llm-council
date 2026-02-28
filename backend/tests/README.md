# LLM Council Tests

This directory contains tests organized by scope.

## Structure

```
tests/
├── README.md              # This file
├── conftest.py           # Shared pytest fixtures and configuration
├── integration/          # Integration tests (direct function calls)
│   ├── __init__.py
│   └── test_council.py   # Tests for council.py core logic
└── e2e/                  # End-to-end tests (HTTP API)
    ├── __init__.py
    └── test_api.py       # Tests for FastAPI endpoints
```

## Test Types

### Integration Tests (`integration/`)

These tests call functions directly without going through HTTP:
- Test `stage1_collect_responses()` directly
- Test `stage2_collect_rankings()` with mocks
- Test `stage3_synthesize_final()` with fixtures
- Fast, isolated, no server needed

**When to add tests here:**
- Testing business logic
- Testing data transformations
- Testing the 3-stage pipeline

**Run integration tests only:**
```bash
pytest backend/tests/integration/ -v
```

### E2E Tests (`e2e/`)

These tests hit the FastAPI HTTP endpoints:
- Test `POST /api/conversations`
- Test `POST /api/conversations/{id}/message`
- Test request/response serialization
- Test CORS, error handling, streaming

**When to add tests here:**
- Testing API contracts
- Testing routing
- Testing full request lifecycle

**Run E2E tests only:**
```bash
pytest backend/tests/e2e/ -v
```

## Running Tests

### All tests
```bash
pytest backend/tests/ -v
```

### With coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

### Specific test file
```bash
pytest backend/tests/integration/test_council.py -v
```

### Specific test class
```bash
pytest backend/tests/integration/test_council.py::TestStage1CollectResponses -v
```

### Specific test method
```bash
pytest backend/tests/integration/test_council.py::TestStage1CollectResponses::test_stage1_calls_all_models -v
```

## Mocking Strategy

### Integration Tests
- Mock `query_model()` to avoid actual LLM calls
- Use fixtures for sample data
- Test logic in isolation

### E2E Tests
- Mock `run_full_council()` and related functions
- Test HTTP layer separately from business logic
- Verify response structure and status codes

## Fixtures

Common fixtures are defined in `conftest.py`:
- `client` - FastAPI TestClient
- `mock_query_model` - Async mock for LLM queries
- `sample_stage1_results` - Sample stage 1 data
- `sample_stage2_results` - Sample stage 2 data

## Adding New Tests

1. Decide the scope:
   - Testing internal logic? → Add to `integration/`
   - Testing API behavior? → Add to `e2e/`

2. Use descriptive test names:
   - `test_stage1_handles_model_failure`
   - `test_send_message_to_nonexistent_conversation`

3. Group related tests in classes:
   ```python
   class TestStage2CollectRankings:
       def test_anonymization_mapping(self): ...
       def test_ranking_parsing(self): ...
   ```

4. Mock external dependencies appropriately
