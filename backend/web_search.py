"""Web search integration for Ollama API."""

import asyncio
import os
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import httpx


@dataclass
class SearchResult:
    """Single web search result."""
    title: str
    url: str
    content: str


@dataclass
class WebSearchResults:
    """Collection of search results."""
    query: str
    results: List[SearchResult]


async def web_search(
    query: str,
    max_results: int = 5,
    api_key: Optional[str] = None
) -> Optional[WebSearchResults]:
    """
    Perform a single web search using Ollama's web search API.

    Args:
        query: Search query string
        max_results: Maximum number of results (default 5, max 10)
        api_key: Ollama API key (defaults to OLLAMA_API_KEY env var)

    Returns:
        WebSearchResults object or None if search fails
    """
    api_key = api_key or os.getenv("OLLAMA_API_KEY", os.getenv("OLLAMA_TOKEN", ""))

    if not api_key:
        print("WARNING: No OLLAMA_API_KEY set, web search disabled")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "max_results": min(max_results, 10),  # Cap at 10
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://ollama.com/api/web_search",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            results = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    content=r.get("content", "")
                )
                for r in data.get("results", [])
            ]

            return WebSearchResults(query=query, results=results)

    except httpx.HTTPStatusError as e:
        print(f"Web search HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        return None
    except httpx.RequestError as e:
        print(f"Web search request error: {type(e).__name__}: {e}")
        return None
    except Exception as e:
        print(f"Web search error: {type(e).__name__}: {e}")
        return None


async def web_fetch(
    url: str,
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch full content from a URL using Ollama's web fetch API.

    Args:
        url: URL to fetch
        api_key: Ollama API key (defaults to OLLAMA_API_KEY env var)

    Returns:
        Dict with 'title', 'content', 'links' or None if fetch fails
    """
    api_key = api_key or os.getenv("OLLAMA_API_KEY", os.getenv("OLLAMA_TOKEN", ""))

    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {"url": url}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://ollama.com/api/web_fetch",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        print(f"Web fetch error for {url}: {type(e).__name__}: {e}")
        return None


def generate_search_queries(user_query: str, num_queries: int = 3) -> List[str]:
    """
    Generate multiple search queries from a user question.
    Creates variations to get diverse perspectives.

    Args:
        user_query: Original user question
        num_queries: Number of search queries to generate (1-5)

    Returns:
        List of search query strings
    """
    num_queries = max(1, min(num_queries, 5))

    # If the query is already simple/short, just use it
    if len(user_query.split()) <= 4 and num_queries == 1:
        return [user_query]

    queries = [user_query]  # Always include original

    # Generate variations based on query type
    query_lower = user_query.lower()

    # Technical/code questions
    if any(kw in query_lower for kw in ["code", "programming", "error", "bug", "api", "function"]):
        variations = [
            f"{user_query} documentation",
            f"{user_query} tutorial example",
            f"{user_query} best practices 2025",
            f"how to fix {user_query}",
        ]
    # News/current events
    elif any(kw in query_lower for kw in ["news", "latest", "recent", "update", "2025", "2026"]):
        variations = [
            f"{user_query} latest news",
            f"{user_query} recent developments",
            f"{user_query} update 2025",
            f"{user_query} official announcement",
        ]
    # How-to questions
    elif query_lower.startswith(("how ", "what ", "why ", "when ", "where ", "who ", "is ", "can ", "should ")):
        variations = [
            f"{user_query} explained",
            f"{user_query} guide",
            f"{user_query} tutorial",
            f"{user_query} expert opinion",
        ]
    # Comparison/decision questions
    elif any(kw in query_lower for kw in ["vs", "versus", "compare", "difference", "better", "best"]):
        variations = [
            f"{user_query} comparison 2025",
            f"{user_query} review",
            f"{user_query} pros and cons",
            f"{user_query} expert analysis",
        ]
    # General questions
    else:
        variations = [
            f"{user_query} overview",
            f"{user_query} detailed guide",
            f"{user_query} examples",
            f"{user_query} explained simply",
        ]

    # Add variations until we reach num_queries
    for var in variations:
        if len(queries) >= num_queries:
            break
        if var not in queries:
            queries.append(var)

    return queries[:num_queries]


def deduplicate_results(results_list: List[WebSearchResults]) -> List[SearchResult]:
    """
    Deduplicate search results from multiple queries.

    Args:
        results_list: List of WebSearchResults from different queries

    Returns:
        List of unique SearchResult objects
    """
    seen_urls: Set[str] = set()
    unique_results: List[SearchResult] = []

    for search_results in results_list:
        if not search_results:
            continue
        for result in search_results.results:
            # Normalize URL for deduplication
            url = result.url.rstrip('/').lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

    return unique_results


def format_search_context(
    results: List[SearchResult],
    max_chars: int = 8000
) -> str:
    """
    Format search results into context string for LLM prompts.

    Args:
        results: List of SearchResult objects
        max_chars: Maximum characters to include (to fit context window)

    Returns:
        Formatted context string
    """
    if not results:
        return ""

    context_parts = ["## Web Search Results\n"]

    for i, result in enumerate(results, 1):
        entry = f"\n### Result {i}: {result.title}\n"
        entry += f"Source: {result.url}\n"
        entry += f"{result.content}\n"
        context_parts.append(entry)

    full_context = "\n".join(context_parts)

    # Truncate if too long, but try to keep complete results
    if len(full_context) > max_chars:
        # Keep the header and as many complete results as possible
        truncated = context_parts[0]
        for part in context_parts[1:]:
            if len(truncated) + len(part) <= max_chars:
                truncated += part
            else:
                # Add a note about truncation
                remaining = len(context_parts) - context_parts.index(part)
                truncated += f"\n\n[Note: {remaining} more search results omitted due to length constraints]"
                break
        return truncated

    return full_context


async def perform_web_search_for_query(
    user_query: str,
    num_searches: int = 3,
    max_results_per_search: int = 5,
    fetch_full_content: bool = False
) -> Optional[str]:
    """
    Perform multiple web searches and return formatted context.

    This is the main entry point for web search in the council flow.

    Args:
        user_query: The user's original question
        num_searches: Number of different search queries to run (1-5)
        max_results_per_search: Results per search query (1-10)
        fetch_full_content: Whether to fetch full content from top results

    Returns:
        Formatted search context string or empty string if disabled/failed
    """
    # Check if web search is enabled
    if os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "false":
        return ""

    # Generate search queries
    search_queries = generate_search_queries(user_query, num_searches)
    print(f"Performing {len(search_queries)} web searches for: {search_queries}")

    # Perform searches in parallel
    search_tasks = [
        web_search(query, max_results_per_search)
        for query in search_queries
    ]
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

    # Filter out failures and exceptions
    valid_results = [
        r for r in search_results
        if isinstance(r, WebSearchResults) and r.results
    ]

    if not valid_results:
        print("No web search results found")
        return ""

    # Deduplicate results
    unique_results = deduplicate_results(valid_results)
    print(f"Found {len(unique_results)} unique search results")

    # Optionally fetch full content from top results
    if fetch_full_content and unique_results:
        top_results = unique_results[:3]  # Fetch top 3
        fetch_tasks = [web_fetch(r.url) for r in top_results]
        fetched_contents = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        # Enhance results with full content where available
        for i, (result, fetched) in enumerate(zip(top_results, fetched_contents)):
            if isinstance(fetched, dict) and fetched.get("content"):
                # Use full content but cap length
                full_content = fetched["content"]
                if len(full_content) > 2000:
                    full_content = full_content[:2000] + "..."
                unique_results[i] = SearchResult(
                    title=result.title,
                    url=result.url,
                    content=f"{result.content}\n\n[Full content]: {full_content}"
                )

    # Format context
    context = format_search_context(unique_results)

    return context


# Convenience function for sync usage
def search_sync(
    user_query: str,
    num_searches: int = 3,
    max_results_per_search: int = 5
) -> str:
    """Synchronous wrapper for perform_web_search_for_query."""
    return asyncio.run(perform_web_search_for_query(
        user_query,
        num_searches,
        max_results_per_search
    ))
