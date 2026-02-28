"""Tests for web search functionality."""

import pytest
from backend.web_search import (
    generate_search_queries,
    deduplicate_results,
    format_search_context,
    SearchResult,
    WebSearchResults,
)


class TestGenerateSearchQueries:
    """Test search query generation."""

    def test_single_word_query(self):
        """Test simple query returns variations."""
        queries = generate_search_queries("Python", 3)
        assert len(queries) == 3
        assert "Python" in queries[0]

    def test_technical_query(self):
        """Test technical query generates appropriate variations."""
        queries = generate_search_queries("How to fix TypeError in Python?", 3)
        assert len(queries) == 3
        assert any("documentation" in q.lower() for q in queries)

    def test_news_query(self):
        """Test news query generates news-specific variations."""
        queries = generate_search_queries("Latest AI news 2025", 3)
        assert len(queries) == 3
        assert any("news" in q.lower() or "recent" in q.lower() for q in queries)

    def test_comparison_query(self):
        """Test comparison query generates comparison variations."""
        queries = generate_search_queries("React vs Vue", 3)
        assert len(queries) == 3

    def test_respects_num_queries_limit(self):
        """Test that num_queries is respected."""
        queries = generate_search_queries("Test query", 1)
        assert len(queries) == 1

        queries = generate_search_queries("Test query", 5)
        assert len(queries) <= 5


class TestDeduplicateResults:
    """Test result deduplication."""

    def test_removes_duplicate_urls(self):
        """Test that duplicate URLs are removed."""
        results = [
            WebSearchResults(
                query="test",
                results=[
                    SearchResult(title="A", url="https://example.com", content="Content A"),
                    SearchResult(title="B", url="https://example.com", content="Content B"),
                ]
            ),
            WebSearchResults(
                query="test2",
                results=[
                    SearchResult(title="C", url="https://example.com/page", content="Content C"),
                ]
            )
        ]

        unique = deduplicate_results(results)
        assert len(unique) == 2

    def test_handles_empty_results(self):
        """Test handling of empty results."""
        results = [
            WebSearchResults(query="test", results=[]),
            WebSearchResults(query="test2", results=[
                SearchResult(title="A", url="https://example.com", content="Content"),
            ])
        ]

        unique = deduplicate_results(results)
        assert len(unique) == 1

    def test_handles_none_results(self):
        """Test handling of None results."""
        results = [
            None,
            WebSearchResults(query="test", results=[
                SearchResult(title="A", url="https://example.com", content="Content"),
            ])
        ]

        unique = deduplicate_results(results)
        assert len(unique) == 1


class TestFormatSearchContext:
    """Test context formatting."""

    def test_basic_formatting(self):
        """Test basic context formatting."""
        results = [
            SearchResult(title="Test Title", url="https://example.com", content="Test content"),
        ]

        context = format_search_context(results)
        assert "## Web Search Results" in context
        assert "Test Title" in context
        assert "https://example.com" in context
        assert "Test content" in context

    def test_empty_results(self):
        """Test formatting with no results."""
        context = format_search_context([])
        assert context == ""

    def test_truncation(self):
        """Test context truncation."""
        results = [
            SearchResult(title="A" * 1000, url="https://example.com", content="B" * 10000),
        ]

        context = format_search_context(results, max_chars=100)
        assert len(context) <= 200  # Some buffer for truncation message

    def test_multiple_results(self):
        """Test formatting multiple results."""
        results = [
            SearchResult(title=f"Title {i}", url=f"https://example{i}.com", content=f"Content {i}")
            for i in range(3)
        ]

        context = format_search_context(results)
        assert "Result 1:" in context
        assert "Result 2:" in context
        assert "Result 3:" in context
