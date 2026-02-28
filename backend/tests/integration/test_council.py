"""Integration tests for LLM Council core logic.

These tests call council functions directly (no HTTP layer).
They test the 3-stage pipeline with various configurations.
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.council import (
    stage1_collect_responses,
    stage2_collect_rankings,
    stage3_synthesize_final,
    run_full_council,
    calculate_aggregate_rankings,
    parse_ranking_from_text,
)


@pytest.fixture
def mock_query_model():
    """Mock the query_model function to return predictable responses."""
    async def _mock_query(model, messages):
        # Return a predictable response based on model name
        content = messages[-1]["content"] if messages else ""
        return {
            "content": f"Response from {model}: {content[:50]}...",
            "reasoning_details": None
        }
    return _mock_query


@pytest.fixture
def mock_query_models_parallel():
    """Mock the query_models_parallel function to return predictable responses."""
    async def _mock_query_parallel(models, messages):
        # Return a dict of model -> response
        return {
            model: {
                "content": f"Response from {model}",
                "reasoning_details": None
            }
            for model in models
        }
    return _mock_query_parallel


@pytest.fixture
def sample_stage1_results():
    """Sample stage 1 results for testing."""
    return [
        {"model": "model-a", "response": "Paris is the capital of France. It is known for the Eiffel Tower."},
        {"model": "model-b", "response": "The capital of France is Paris, a beautiful city on the Seine River."},
        {"model": "model-c", "response": "Paris is France's capital, famous for art, culture, and cuisine."},
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
        {
            "model": "model-c",
            "ranking": "FINAL RANKING:\n1. Response C\n2. Response B\n3. Response A",
            "parsed_ranking": ["Response C", "Response B", "Response A"]
        },
    ]


class TestStage1CollectResponses:
    """Tests for Stage 1: Collecting initial responses."""

    @pytest.mark.asyncio
    async def test_stage1_calls_all_models(self, mock_query_models_parallel):
        """Stage 1 should query all configured models."""
        with patch('backend.council.query_models_parallel', side_effect=mock_query_models_parallel):
            with patch('backend.council.COUNCIL_MODELS', ['model-a', 'model-b', 'model-c']):
                results = await stage1_collect_responses("Test query")

        assert len(results) == 3
        assert all(r['model'] in ['model-a', 'model-b', 'model-c'] for r in results)
        assert all('response' in r for r in results)

    @pytest.mark.asyncio
    async def test_stage1_handles_model_failure(self, mock_query_models_parallel):
        """Stage 1 should continue if some models fail."""
        async def failing_query_parallel(models, messages):
            # Return None for model-b, valid responses for others
            return {
                model: None if model == 'model-b' else {"content": f"Response from {model}"}
                for model in models
            }

        with patch('backend.council.query_models_parallel', side_effect=failing_query_parallel):
            with patch('backend.council.COUNCIL_MODELS', ['model-a', 'model-b', 'model-c']):
                results = await stage1_collect_responses("Test query")

        # Should have 2 successful results (model-b failed)
        assert len(results) == 2
        assert 'model-b' not in [r['model'] for r in results]


class TestStage2CollectRankings:
    """Tests for Stage 2: Anonymized peer review."""

    @pytest.mark.asyncio
    async def test_anonymization_mapping(self, mock_query_model, sample_stage1_results):
        """Stage 2 should create correct label-to-model mapping."""
        async def capture_prompt(model, messages):
            # Return the ranking we expect
            return {"content": "FINAL RANKING:\n1. Response A\n2. Response B\n3. Response C"}

        with patch('backend.council.query_model', side_effect=capture_prompt):
            rankings, label_to_model = await stage2_collect_rankings(
                "What is the capital of France?",
                sample_stage1_results
            )

        # Verify mapping
        assert len(label_to_model) == 3
        assert all(label in label_to_model for label in ['Response A', 'Response B', 'Response C'])
        # Verify each model appears exactly once in mapping
        models_in_mapping = set(label_to_model.values())
        assert models_in_mapping == {'model-a', 'model-b', 'model-c'}

    @pytest.mark.asyncio
    async def test_ranking_parsing(self, mock_query_models_parallel, sample_stage1_results):
        """Stage 2 should parse rankings correctly."""
        ranking_text = """
        Let me evaluate each response:

        Response A: Good but brief.
        Response B: Comprehensive and accurate.
        Response C: Creative but slightly off-topic.

        FINAL RANKING:
        1. Response B
        2. Response A
        3. Response C
        """

        async def return_rankings(models, messages):
            return {model: {"content": ranking_text} for model in models}

        with patch('backend.council.COUNCIL_MODELS', ['model-a', 'model-b', 'model-c']):
            with patch('backend.council.query_models_parallel', side_effect=return_rankings):
                rankings, label_to_model = await stage2_collect_rankings(
                    "Test query",
                    sample_stage1_results
                )

        assert len(rankings) == 3
        assert all('parsed_ranking' in r for r in rankings)
        assert all(r['parsed_ranking'] == ['Response B', 'Response A', 'Response C'] for r in rankings)


class TestStage3SynthesizeFinal:
    """Tests for Stage 3: Chairman synthesis."""

    @pytest.mark.asyncio
    async def test_stage3_includes_all_context(self, mock_query_model, sample_stage1_results, sample_stage2_results):
        """Stage 3 should receive all stage 1 and 2 results."""
        captured_messages = None

        async def capture_messages(model, messages):
            nonlocal captured_messages
            captured_messages = messages
            return {"content": "Final synthesized answer."}

        with patch('backend.council.query_model', side_effect=capture_messages):
            result = await stage3_synthesize_final(
                "What is the capital of France?",
                sample_stage1_results,
                sample_stage2_results
            )

        assert captured_messages is not None
        # Verify prompt contains stage 1 responses
        prompt = captured_messages[-1]["content"]
        assert "Paris" in prompt or "model-a" in prompt
        # Verify prompt contains rankings
        assert "FINAL RANKING" in prompt or "Ranking" in prompt

    @pytest.mark.asyncio
    async def test_stage3_returns_chairman_model(self, mock_query_model, sample_stage1_results, sample_stage2_results):
        """Stage 3 should identify the chairman model in results."""
        with patch('backend.council.query_model', side_effect=mock_query_model):
            with patch('backend.council.CHAIRMAN_MODEL', 'test-chairman-model'):
                result = await stage3_synthesize_final(
                    "Test query",
                    sample_stage1_results,
                    sample_stage2_results
                )

        assert result['model'] == 'test-chairman-model'
        assert 'response' in result


class TestParseRankingFromText:
    """Tests for ranking text parsing."""

    def test_standard_numbered_format(self):
        """Parse standard '1. Response A' format."""
        text = """
        Some evaluation text.

        FINAL RANKING:
        1. Response C
        2. Response A
        3. Response B
        """
        result = parse_ranking_from_text(text)
        assert result == ['Response C', 'Response A', 'Response B']

    def test_plain_list_format(self):
        """Parse plain list without numbers."""
        text = """
        FINAL RANKING:
        Response B
        Response A
        Response C
        """
        result = parse_ranking_from_text(text)
        assert result == ['Response B', 'Response A', 'Response C']

    def test_no_final_ranking_header(self):
        """Handle missing FINAL RANKING header."""
        text = "Just some random text without a ranking."
        result = parse_ranking_from_text(text)
        # Should fallback to finding Response X patterns in order
        assert isinstance(result, list)


class TestCalculateAggregateRankings:
    """Tests for aggregate ranking calculation."""

    def test_basic_aggregation(self):
        """Calculate average positions correctly."""
        stage2_results = [
            {"model": "rater-1", "ranking": "FINAL RANKING:\n1. Response A\n2. Response B", "parsed_ranking": ["Response A", "Response B"]},
            {"model": "rater-2", "ranking": "FINAL RANKING:\n1. Response B\n2. Response A", "parsed_ranking": ["Response B", "Response A"]},
        ]
        label_to_model = {"Response A": "model-a", "Response B": "model-b"}

        result = calculate_aggregate_rankings(stage2_results, label_to_model)

        # Response A: positions 1, 2 -> avg 1.5
        # Response B: positions 2, 1 -> avg 1.5
        assert len(result) == 2
        models = [r["model"] for r in result]
        assert "model-a" in models
        assert "model-b" in models

        # Find model-a and check its average rank
        model_a = next(r for r in result if r["model"] == "model-a")
        assert model_a["average_rank"] == 1.5
        assert model_a["rankings_count"] == 2

    def test_partial_rankings(self):
        """Handle incomplete rankings gracefully."""
        stage2_results = [
            {"model": "rater-1", "ranking": "FINAL RANKING:\n1. Response A", "parsed_ranking": ["Response A"]},
            {"model": "rater-2", "ranking": "FINAL RANKING:\n1. Response B\n2. Response A", "parsed_ranking": ["Response B", "Response A"]},
        ]
        label_to_model = {"Response A": "model-a", "Response B": "model-b"}

        result = calculate_aggregate_rankings(stage2_results, label_to_model)

        # Should not crash and should have results for both
        assert len(result) == 2
        models = [r["model"] for r in result]
        assert "model-a" in models
        assert "model-b" in models


class TestFullCouncilPipeline:
    """Tests for the complete 3-stage pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline_flow(self, mock_query_model):
        """Test complete pipeline with mocked models."""
        stage1_response = {"content": "Test response"}
        ranking_text = "FINAL RANKING:\n1. Response A\n2. Response B"
        stage3_response = {"content": "Final answer"}

        with patch('backend.council.COUNCIL_MODELS', ['model-a', 'model-b']):
            with patch('backend.council.CHAIRMAN_MODEL', 'chairman-model'):
                # Mock stage 1
                with patch('backend.council.query_models_parallel', return_value={
                    'model-a': stage1_response,
                    'model-b': stage1_response
                }):
                    # Mock stage 2
                    with patch('backend.openrouter.query_model', return_value={"content": ranking_text}):
                        # Mock stage 3
                        with patch('backend.council.query_model', return_value=stage3_response):
                            stage1, stage2, stage3, metadata = await run_full_council("Test question")

        assert len(stage1) == 2
        assert len(stage2) == 2
        assert stage3['model'] == 'chairman-model'
        assert 'response' in stage3
        assert 'label_to_model' in metadata
        assert 'aggregate_rankings' in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
