"""End-to-end tests for LLM Council API.

These tests hit the actual FastAPI endpoints via HTTP.
They test the complete request/response cycle including:
- Routing
- Request/Response serialization
- CORS
- Error handling
- Streaming endpoints
"""

import pytest
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from backend.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_council_functions():
    """Mock all council functions to return predictable data."""
    stage1_results = [
        {"model": "model-a", "response": "Test response from model A"},
        {"model": "model-b", "response": "Test response from model B"},
    ]

    stage2_results = [
        {
            "model": "model-a",
            "ranking": "FINAL RANKING:\\n1. Response B\\n2. Response A",
            "parsed_ranking": ["Response B", "Response A"]
        },
        {
            "model": "model-b",
            "ranking": "FINAL RANKING:\\n1. Response A\\n2. Response B",
            "parsed_ranking": ["Response A", "Response B"]
        },
    ]

    stage3_result = {
        "model": "chairman-model",
        "response": "Final synthesized answer."
    }

    metadata = {
        "label_to_model": {"Response A": "model-a", "Response B": "model-b"},
        "aggregate_rankings": {
            "model-a": {"average_position": 1.5, "votes": 2},
            "model-b": {"average_position": 1.5, "votes": 2}
        }
    }

    return stage1_results, stage2_results, stage3_result, metadata


class TestHealthAndRoot:
    """Tests for basic health check endpoints."""

    def test_root_endpoint(self, client):
        """Root endpoint should return service status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data


class TestConversationEndpoints:
    """Tests for conversation CRUD operations."""

    def test_create_conversation(self, client):
        """POST /api/conversations should create a new conversation."""
        response = client.post("/api/conversations", json={})
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "created_at" in data
        assert "title" in data
        assert data["messages"] == []

    def test_list_conversations(self, client):
        """GET /api/conversations should list all conversations."""
        # Create a conversation first
        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        response = client.get("/api/conversations")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check structure
        assert "id" in data[0]
        assert "title" in data[0]
        assert "message_count" in data[0]

    def test_get_conversation(self, client):
        """GET /api/conversations/{id} should return specific conversation."""
        # Create a conversation
        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        response = client.get(f"/api/conversations/{conv_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == conv_id
        assert "messages" in data

    def test_get_nonexistent_conversation(self, client):
        """GET /api/conversations/{id} should 404 for unknown ID."""
        response = client.get("/api/conversations/nonexistent-id-12345")
        assert response.status_code == 404


class TestMessageEndpoints:
    """Tests for message sending and council processing."""

    def test_send_message_basic_flow(self, client, mock_council_functions):
        """POST /api/conversations/{id}/message should process through all stages."""
        stage1, stage2, stage3, metadata = mock_council_functions

        # Create a conversation
        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        # Mock the council functions
        with patch('backend.main.run_full_council', return_value=(stage1, stage2, stage3, metadata)):
            with patch('backend.main.generate_conversation_title', return_value="Test Title"):
                response = client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "What is the capital of France?"}
                )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "stage1" in data
        assert "stage2" in data
        assert "stage3" in data
        assert "metadata" in data

        # Verify stage 1 structure
        assert len(data["stage1"]) == 2
        assert data["stage1"][0]["model"] == "model-a"

        # Verify stage 2 structure
        assert len(data["stage2"]) == 2
        assert "parsed_ranking" in data["stage2"][0]

        # Verify stage 3 structure
        assert data["stage3"]["model"] == "chairman-model"

        # Verify metadata
        assert "label_to_model" in data["metadata"]
        assert "aggregate_rankings" in data["metadata"]

    def test_send_message_to_nonexistent_conversation(self, client):
        """POST /api/conversations/{id}/message should 404 for unknown conversation."""
        response = client.post(
            "/api/conversations/nonexistent-id-12345/message",
            json={"content": "Hello"}
        )
        assert response.status_code == 404

    def test_send_message_title_generation(self, client, mock_council_functions):
        """First message should trigger title generation."""
        stage1, stage2, stage3, metadata = mock_council_functions

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(stage1, stage2, stage3, metadata)):
            with patch('backend.main.generate_conversation_title', return_value="France Capital") as mock_title:
                client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "What is the capital of France?"}
                )

                # Verify title generation was called
                mock_title.assert_called_once()

    def test_conversation_persistence(self, client, mock_council_functions):
        """Messages should be persisted to storage."""
        stage1, stage2, stage3, metadata = mock_council_functions

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(stage1, stage2, stage3, metadata)):
            client.post(
                f"/api/conversations/{conv_id}/message",
                json={"content": "Test message"}
            )

        # Get conversation and verify messages were stored
        response = client.get(f"/api/conversations/{conv_id}")
        data = response.json()

        assert len(data["messages"]) == 2  # User message + assistant message
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"


class TestStreamingEndpoint:
    """Tests for the streaming message endpoint."""

    def test_streaming_endpoint_structure(self, client, mock_council_functions):
        """Streaming endpoint should return SSE with correct events."""
        stage1, stage2, stage3, metadata = mock_council_functions

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.stage1_collect_responses', return_value=stage1):
            with patch('backend.main.stage2_collect_rankings', return_value=(stage2, metadata["label_to_model"])):
                with patch('backend.main.calculate_aggregate_rankings', return_value=metadata["aggregate_rankings"]):
                    with patch('backend.main.stage3_synthesize_final', return_value=stage3):
                        with patch('backend.main.generate_conversation_title', return_value="Test"):
                            response = client.post(
                                f"/api/conversations/{conv_id}/message/stream",
                                json={"content": "Test message"}
                            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Parse SSE events - SSE format uses \n\n as event delimiter
        content = response.content.decode('utf-8')
        # Split by double newline to get individual events
        events = [e.strip() for e in content.split('\n\n') if e.strip()]

        # Should have multiple events
        assert len(events) > 0

        # Check event types - each event should have 'data: {...}'
        event_types = []
        for event in events:
            for line in event.split('\n'):
                if line.startswith('data:'):
                    try:
                        data = json.loads(line.replace('data:', '').strip())
                        event_types.append(data.get('type'))
                    except json.JSONDecodeError:
                        pass

        assert 'stage1_start' in event_types
        assert 'stage1_complete' in event_types
        assert 'stage2_start' in event_types
        assert 'stage2_complete' in event_types
        assert 'stage3_start' in event_types
        assert 'stage3_complete' in event_types
        assert 'complete' in event_types


class TestCorsConfiguration:
    """Tests for CORS middleware configuration."""

    def test_cors_preflight(self, client):
        """Should handle CORS preflight requests."""
        response = client.options(
            "/api/conversations",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_invalid_json_body(self, client):
        """Should handle invalid JSON gracefully."""
        response = client.post(
            "/api/conversations/test-id/message",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # FastAPI validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
