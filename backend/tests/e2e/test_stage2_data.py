"""E2E tests for Stage 2 data structure validation.

These tests verify that the API returns data in the correct format
for the Stage2 component to render without errors.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from backend.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestStage2DataStructure:
    """Tests that Stage 2 data is returned in the expected format."""

    def test_stage2_rankings_have_required_fields(self, client):
        """Each ranking must have model, ranking, and parsed_ranking fields."""
        stage1_results = [
            {"model": "openai/gpt-4", "response": "Test response 1"},
            {"model": "anthropic/claude", "response": "Test response 2"},
        ]

        stage2_results = [
            {
                "model": "openai/gpt-4",
                "ranking": "FINAL RANKING:\n1. Response A\n2. Response B",
                "parsed_ranking": ["Response A", "Response B"]
            },
            {
                "model": "anthropic/claude",
                "ranking": "FINAL RANKING:\n1. Response B\n2. Response A",
                "parsed_ranking": ["Response B", "Response A"]
            }
        ]

        stage3_result = {
            "model": "google/gemini",
            "response": "Final synthesized answer."
        }

        metadata = {
            "label_to_model": {"Response A": "openai/gpt-4", "Response B": "anthropic/claude"},
            "aggregate_rankings": [
                {"model": "openai/gpt-4", "average_rank": 1.5, "rankings_count": 2},
                {"model": "anthropic/claude", "average_rank": 1.5, "rankings_count": 2}
            ],
            "web_search_enabled": True,
            "web_search_context_length": 0
        }

        # Create conversation
        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(
            stage1_results, stage2_results, stage3_result, metadata
        )):
            with patch('backend.main.generate_conversation_title', return_value="Test"):
                response = client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "Test question"}
                )

        assert response.status_code == 200
        data = response.json()

        # Verify stage2 structure
        assert "stage2" in data
        assert len(data["stage2"]) == 2

        for ranking in data["stage2"]:
            # Required fields for Stage2 component
            assert "model" in ranking
            assert isinstance(ranking["model"], str)
            assert ranking["model"] != ""  # Should not be empty

            assert "ranking" in ranking
            assert isinstance(ranking["ranking"], str)

            assert "parsed_ranking" in ranking
            assert isinstance(ranking["parsed_ranking"], list)

    def test_stage2_handles_model_with_slash_format(self, client):
        """Models should be in provider/model format."""
        stage1_results = [{"model": "test", "response": "test"}]

        stage2_results = [
            {
                "model": "openai/gpt-4-turbo",  # Full format
                "ranking": "FINAL RANKING:\n1. Response A",
                "parsed_ranking": ["Response A"]
            }
        ]

        stage3_result = {"model": "google/gemini", "response": "test"}

        metadata = {
            "label_to_model": {"Response A": "openai/gpt-4-turbo"},
            "aggregate_rankings": [
                {"model": "openai/gpt-4-turbo", "average_rank": 1.0, "rankings_count": 1}
            ],
            "web_search_enabled": False,
            "web_search_context_length": 0
        }

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(
            stage1_results, stage2_results, stage3_result, metadata
        )):
            with patch('backend.main.generate_conversation_title', return_value="Test"):
                response = client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "Test"}
                )

        data = response.json()
        ranking = data["stage2"][0]

        # Model should contain a slash (provider/model format)
        assert "/" in ranking["model"]
        parts = ranking["model"].split("/")
        assert len(parts) == 2
        assert parts[0] == "openai"
        assert parts[1] == "gpt-4-turbo"

    def test_stage2_metadata_has_label_to_model_mapping(self, client):
        """Metadata must include label_to_model mapping for de-anonymization."""
        stage1_results = [
            {"model": "model-a", "response": "Response A content"},
            {"model": "model-b", "response": "Response B content"},
        ]

        stage2_results = [
            {
                "model": "model-a",
                "ranking": "FINAL RANKING:\n1. Response B\n2. Response A",
                "parsed_ranking": ["Response B", "Response A"]
            }
        ]

        stage3_result = {"model": "chairman", "response": "Final"}

        metadata = {
            "label_to_model": {"Response A": "model-a", "Response B": "model-b"},
            "aggregate_rankings": [],
            "web_search_enabled": True,
            "web_search_context_length": 100
        }

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(
            stage1_results, stage2_results, stage3_result, metadata
        )):
            with patch('backend.main.generate_conversation_title', return_value="Test"):
                response = client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "Test"}
                )

        data = response.json()
        assert "metadata" in data
        assert "label_to_model" in data["metadata"]

        label_to_model = data["metadata"]["label_to_model"]
        assert isinstance(label_to_model, dict)
        assert "Response A" in label_to_model
        assert "Response B" in label_to_model

    def test_stage2_aggregate_rankings_structure(self, client):
        """Aggregate rankings must have required fields."""
        stage1_results = [{"model": "test", "response": "test"}]
        stage2_results = [{"model": "test", "ranking": "test", "parsed_ranking": []}]
        stage3_result = {"model": "test", "response": "test"}

        metadata = {
            "label_to_model": {},
            "aggregate_rankings": [
                {
                    "model": "openai/gpt-4",
                    "average_rank": 1.33,
                    "rankings_count": 3
                },
                {
                    "model": "anthropic/claude",
                    "average_rank": 1.67,
                    "rankings_count": 3
                }
            ],
            "web_search_enabled": True,
            "web_search_context_length": 0
        }

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(
            stage1_results, stage2_results, stage3_result, metadata
        )):
            with patch('backend.main.generate_conversation_title', return_value="Test"):
                response = client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "Test"}
                )

        data = response.json()
        aggregate = data["metadata"]["aggregate_rankings"]

        assert len(aggregate) == 2
        for agg in aggregate:
            assert "model" in agg
            assert isinstance(agg["model"], str)
            assert agg["model"] != ""

            assert "average_rank" in agg
            assert isinstance(agg["average_rank"], (int, float))

            assert "rankings_count" in agg
            assert isinstance(agg["rankings_count"], int)

    def test_stage2_parsed_ranking_is_array(self, client):
        """parsed_ranking should always be an array."""
        stage1_results = [{"model": "test", "response": "test"}]

        # Empty parsed ranking
        stage2_results = [
            {
                "model": "test-model",
                "ranking": "Could not rank",
                "parsed_ranking": []
            }
        ]

        stage3_result = {"model": "chairman", "response": "test"}
        metadata = {
            "label_to_model": {},
            "aggregate_rankings": [],
            "web_search_enabled": False,
            "web_search_context_length": 0
        }

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.run_full_council', return_value=(
            stage1_results, stage2_results, stage3_result, metadata
        )):
            with patch('backend.main.generate_conversation_title', return_value="Test"):
                response = client.post(
                    f"/api/conversations/{conv_id}/message",
                    json={"content": "Test"}
                )

        data = response.json()
        ranking = data["stage2"][0]

        assert "parsed_ranking" in ranking
        assert isinstance(ranking["parsed_ranking"], list)
        assert len(ranking["parsed_ranking"]) == 0


class TestStreamingStage2Data:
    """Tests for streaming endpoint Stage 2 data format."""

    def test_streaming_includes_stage2_complete_event(self, client):
        """Streaming should include stage2_complete event with correct data."""
        stage1_results = [{"model": "test", "response": "test"}]
        stage2_results = [
            {
                "model": "openai/gpt-4",
                "ranking": "FINAL RANKING:\n1. Response A",
                "parsed_ranking": ["Response A"]
            }
        ]

        label_to_model = {"Response A": "openai/gpt-4"}
        aggregate_rankings = [
            {"model": "openai/gpt-4", "average_rank": 1.0, "rankings_count": 1}
        ]

        create_response = client.post("/api/conversations", json={})
        conv_id = create_response.json()["id"]

        with patch('backend.main.stage1_collect_responses', return_value=stage1_results):
            with patch('backend.main.stage2_collect_rankings', return_value=(stage2_results, label_to_model)):
                with patch('backend.main.calculate_aggregate_rankings', return_value=aggregate_rankings):
                    with patch('backend.main.stage3_synthesize_final', return_value={"model": "test", "response": "test"}):
                        with patch('backend.main.generate_conversation_title', return_value="Test"):
                            response = client.post(
                                f"/api/conversations/{conv_id}/message/stream",
                                json={"content": "Test"}
                            )

        assert response.status_code == 200
        content = response.content.decode('utf-8')

        # Parse SSE events
        events = [e.strip() for e in content.split('\n\n') if e.strip()]

        # Find stage2_complete event
        stage2_event = None
        for event in events:
            for line in event.split('\n'):
                if line.startswith('data:'):
                    try:
                        data = json.loads(line.replace('data:', '').strip())
                        if data.get('type') == 'stage2_complete':
                            stage2_event = data
                            break
                    except json.JSONDecodeError:
                        pass

        assert stage2_event is not None
        assert 'data' in stage2_event
        assert isinstance(stage2_event['data'], list)
        assert len(stage2_event['data']) == 1

        # Verify structure
        ranking = stage2_event['data'][0]
        assert 'model' in ranking
        assert 'ranking' in ranking
        assert 'parsed_ranking' in ranking


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
