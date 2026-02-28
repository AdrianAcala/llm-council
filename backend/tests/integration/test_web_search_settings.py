"""Integration tests for web search functionality.

These tests verify that web search can be enabled/disabled per conversation
and that the setting is properly persisted and respected.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import json

from backend.main import app
from backend import storage


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestWebSearchPerConversation:
    """Tests for per-conversation web search toggle."""

    def test_create_conversation_with_web_search_enabled(self, client):
        """Creating a conversation with web_search_enabled should persist it."""
        response = client.post("/api/conversations", json={"web_search_enabled": True})
        assert response.status_code == 200

        data = response.json()
        assert data["settings"]["web_search_enabled"] is True

    def test_create_conversation_with_web_search_disabled(self, client):
        """Creating a conversation with web_search_enabled=false should persist it."""
        response = client.post("/api/conversations", json={"web_search_enabled": False})
        assert response.status_code == 200

        data = response.json()
        assert data["settings"]["web_search_enabled"] is False

    def test_default_web_search_enabled(self, client):
        """Default web_search_enabled should be True when not specified."""
        response = client.post("/api/conversations", json={})
        assert response.status_code == 200

        data = response.json()
        assert data["settings"]["web_search_enabled"] is True

    def test_update_conversation_settings(self, client):
        """PATCH /api/conversations/{id}/settings should update settings."""
        # Create a conversation
        create_response = client.post("/api/conversations", json={"web_search_enabled": True})
        conv_id = create_response.json()["id"]

        # Update settings
        response = client.patch(
            f"/api/conversations/{conv_id}/settings",
            json={"web_search_enabled": False}
        )
        assert response.status_code == 200
        assert response.json()["settings"]["web_search_enabled"] is False

        # Verify by getting conversation
        get_response = client.get(f"/api/conversations/{conv_id}")
        assert get_response.json()["settings"]["web_search_enabled"] is False

    def test_update_settings_nonexistent_conversation(self, client):
        """PATCH settings should 404 for unknown conversation."""
        response = client.patch(
            "/api/conversations/nonexistent-id/settings",
            json={"web_search_enabled": False}
        )
        assert response.status_code == 404


class TestWebSearchInMessageProcessing:
    """Tests that web search setting affects message processing."""

    def test_send_message_respects_web_search_enabled(self, client):
        """When web_search_enabled=True, get_search_context should be called."""
        # Create conversation with web search enabled
        create_response = client.post("/api/conversations", json={"web_search_enabled": True})
        conv_id = create_response.json()["id"]

        mock_stage1 = [{"model": "test", "response": "test"}]
        mock_stage2 = ([], {})
        mock_stage3 = {"model": "chairman", "response": "answer"}
        mock_metadata = {"web_search_enabled": True}

        with patch('backend.main.run_full_council') as mock_run:
            mock_run.return_value = (mock_stage1, mock_stage2, mock_stage3, mock_metadata)

            client.post(
                f"/api/conversations/{conv_id}/message",
                json={"content": "What is AI?"}
            )

            # Verify run_full_council was called with web_search_enabled=True
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            # Check positional or keyword args
            if call_args.kwargs:
                assert call_args.kwargs.get('web_search_enabled') is True
            else:
                # If passed as positional, it's the second arg
                assert len(call_args.args) >= 2
                assert call_args.args[1] is True

    def test_send_message_respects_web_search_disabled(self, client):
        """When web_search_enabled=False, get_search_context should not be called."""
        # Create conversation with web search disabled
        create_response = client.post("/api/conversations", json={"web_search_enabled": False})
        conv_id = create_response.json()["id"]

        mock_stage1 = [{"model": "test", "response": "test"}]
        mock_stage2 = ([], {})
        mock_stage3 = {"model": "chairman", "response": "answer"}
        mock_metadata = {"web_search_enabled": False}

        with patch('backend.main.run_full_council') as mock_run:
            mock_run.return_value = (mock_stage1, mock_stage2, mock_stage3, mock_metadata)

            client.post(
                f"/api/conversations/{conv_id}/message",
                json={"content": "What is AI?"}
            )

            # Verify run_full_council was called with web_search_enabled=False
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            # Check positional or keyword args
            if call_args.kwargs:
                assert call_args.kwargs.get('web_search_enabled') is False
            else:
                # If passed as positional, it's the second arg
                assert len(call_args.args) >= 2
                assert call_args.args[1] is False

    def test_send_message_with_override_enabled(self, client):
        """Request can override conversation setting to enable web search."""
        # Create conversation with web search disabled
        create_response = client.post("/api/conversations", json={"web_search_enabled": False})
        conv_id = create_response.json()["id"]

        mock_stage1 = [{"model": "test", "response": "test"}]
        mock_stage2 = ([], {})
        mock_stage3 = {"model": "chairman", "response": "answer"}
        mock_metadata = {"web_search_enabled": True}

        with patch('backend.main.run_full_council') as mock_run:
            mock_run.return_value = (mock_stage1, mock_stage2, mock_stage3, mock_metadata)

            # Override with web_search_enabled=True
            client.post(
                f"/api/conversations/{conv_id}/message",
                json={"content": "What is AI?", "web_search_enabled": True}
            )

            # Verify web_search_enabled was overridden
            call_args = mock_run.call_args
            # Check positional or keyword args
            if call_args.kwargs:
                assert call_args.kwargs.get('web_search_enabled') is True
            else:
                assert len(call_args.args) >= 2
                assert call_args.args[1] is True

    def test_send_message_with_override_disabled(self, client):
        """Request can override conversation setting to disable web search."""
        # Create conversation with web search enabled
        create_response = client.post("/api/conversations", json={"web_search_enabled": True})
        conv_id = create_response.json()["id"]

        mock_stage1 = [{"model": "test", "response": "test"}]
        mock_stage2 = ([], {})
        mock_stage3 = {"model": "chairman", "response": "answer"}
        mock_metadata = {"web_search_enabled": False}

        with patch('backend.main.run_full_council') as mock_run:
            mock_run.return_value = (mock_stage1, mock_stage2, mock_stage3, mock_metadata)

            # Override with web_search_enabled=False
            client.post(
                f"/api/conversations/{conv_id}/message",
                json={"content": "What is AI?", "web_search_enabled": False}
            )

            # Verify web_search_enabled was overridden
            call_args = mock_run.call_args
            # Check positional or keyword args
            if call_args.kwargs:
                assert call_args.kwargs.get('web_search_enabled') is False
            else:
                assert len(call_args.args) >= 2
                assert call_args.args[1] is False


class TestWebSearchCouncilFunctions:
    """Tests for council.py web search integration."""

    @pytest.mark.asyncio
    async def test_get_search_context_respects_enabled(self):
        """get_search_context should perform search when enabled."""
        from backend.council import get_search_context

        with patch('backend.council.perform_web_search_for_query') as mock_search:
            mock_search.return_value = "Search results"

            result = await get_search_context("test query", web_search_enabled=True)

            mock_search.assert_called_once()
            assert result == "Search results"

    @pytest.mark.asyncio
    async def test_get_search_context_respects_disabled(self):
        """get_search_context should skip search when disabled."""
        from backend.council import get_search_context

        with patch('backend.council.perform_web_search_for_query') as mock_search:
            result = await get_search_context("test query", web_search_enabled=False)

            mock_search.assert_not_called()
            assert result == ""

    @pytest.mark.asyncio
    async def test_run_full_council_passes_web_search_setting(self):
        """run_full_council should pass web_search_enabled to get_search_context."""
        from backend.council import run_full_council

        with patch('backend.council.get_search_context') as mock_get_context:
            mock_get_context.return_value = ""

            with patch('backend.council.stage1_collect_responses', return_value=[]):
                with patch('backend.council.stage2_collect_rankings', return_value=([], {})):
                    with patch('backend.council.calculate_aggregate_rankings', return_value=[]):
                        with patch('backend.council.stage3_synthesize_final', return_value={"model": "test", "response": "test"}):
                            await run_full_council("test", web_search_enabled=False)

            # Verify get_search_context was called with web_search_enabled=False
            mock_get_context.assert_called_once()
            call_args = mock_get_context.call_args
            # web_search_enabled is passed as second positional arg
            assert len(call_args.args) >= 2
            assert call_args.args[1] is False

    @pytest.mark.asyncio
    async def test_run_full_council_metadata_includes_web_search_status(self):
        """run_full_council metadata should reflect web_search_enabled."""
        from backend.council import run_full_council

        # Mock with non-empty stage1 results so it proceeds past the early return
        mock_stage1 = [{"model": "test", "response": "test response"}]

        with patch('backend.council.get_search_context', return_value=""):
            with patch('backend.council.stage1_collect_responses', return_value=mock_stage1):
                with patch('backend.council.stage2_collect_rankings', return_value=([], {})):
                    with patch('backend.council.calculate_aggregate_rankings', return_value=[]):
                        with patch('backend.council.stage3_synthesize_final', return_value={"model": "test", "response": "test"}):
                            _, _, _, metadata = await run_full_council("test", web_search_enabled=True)

            # Metadata should be a dict with web_search_enabled key
            assert isinstance(metadata, dict)
            assert metadata.get("web_search_enabled") is True


class TestWebSearchStorage:
    """Tests for web search setting persistence in storage."""

    def test_storage_includes_settings(self, tmp_path):
        """create_conversation should include settings in stored data."""
        # Temporarily override DATA_DIR
        original_data_dir = storage.DATA_DIR
        storage.DATA_DIR = str(tmp_path / "test_data")

        try:
            conv = storage.create_conversation("test-id", {"web_search_enabled": False})

            # Load from file and verify
            loaded = storage.get_conversation("test-id")
            assert loaded["settings"]["web_search_enabled"] is False
        finally:
            storage.DATA_DIR = original_data_dir

    def test_update_settings_persists(self, tmp_path):
        """update_conversation_settings should persist changes."""
        original_data_dir = storage.DATA_DIR
        storage.DATA_DIR = str(tmp_path / "test_data")

        try:
            # Create conversation
            storage.create_conversation("test-id", {"web_search_enabled": True})

            # Update settings
            storage.update_conversation_settings("test-id", {"web_search_enabled": False})

            # Verify
            loaded = storage.get_conversation("test-id")
            assert loaded["settings"]["web_search_enabled"] is False
        finally:
            storage.DATA_DIR = original_data_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
