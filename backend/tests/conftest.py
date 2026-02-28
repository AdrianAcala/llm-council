"""Shared pytest fixtures and configuration."""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def mock_query_model():
    """Mock the query_model function to return predictable responses."""
    async def _mock_query(model, messages):
        content = messages[-1]["content"] if messages else ""
        return {
            "content": f"Response from {model}: {content[:50]}...",
            "reasoning_details": None
        }
    return _mock_query


@pytest.fixture
def sample_stage1_results():
    """Sample stage 1 results for testing."""
    return [
        {"model": "model-a", "response": "Paris is the capital of France."},
        {"model": "model-b", "response": "The capital of France is Paris."},
        {"model": "model-c", "response": "Paris is France's capital."},
    ]


@pytest.fixture
def sample_stage2_results():
    """Sample stage 2 results with parsed rankings."""
    return [
        {
            "model": "model-a",
            "ranking": "FINAL RANKING:\n1. Response B\n2. Response C\n3. Response A",
            "parsed_ranking": ["Response B", "Response C", "Response A"]
        },
        {
            "model": "model-b",
            "ranking": "FINAL RANKING:\n1. Response B\n2. Response A\n3. Response C",
            "parsed_ranking": ["Response B", "Response A", "Response C"]
        },
    ]


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {
        "label_to_model": {
            "Response A": "model-a",
            "Response B": "model-b",
            "Response C": "model-c"
        },
        "aggregate_rankings": {
            "model-a": {"average_position": 2.0, "votes": 2},
            "model-b": {"average_position": 1.5, "votes": 2},
            "model-c": {"average_position": 2.5, "votes": 2}
        }
    }
