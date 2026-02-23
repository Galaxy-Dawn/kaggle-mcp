"""Discussion tools for Kaggle MCP Server (kagglesdk search + HTML fallback)."""

import logging
import re

import httpx
from mcp.server.fastmcp import FastMCP

from .client import get_client

logger = logging.getLogger(__name__)


def _search_via_sdk(
    query: str = "",
    source_type: str = "",
    page_size: int = 20,
    page_token: str = "",
) -> list[dict]:
    """Search discussions via kagglesdk search API."""
    from kagglesdk.search.services.search_api_service import ListEntitiesRequest
    from kagglesdk.search.types.search_api_service import (
        ApiSearchDiscussionsFilters,
        DocumentType,
        ListEntitiesFilters,
    )

    req = ListEntitiesRequest()
    f = ListEntitiesFilters()
    f.document_types = [DocumentType.TOPIC]
    if query:
        f.query = query

    if source_type:
        from kagglesdk.discussions.types.search_discussions import (
            SearchDiscussionsSourceType,
        )

        df = ApiSearchDiscussionsFilters()
        type_map = {
            "competition": SearchDiscussionsSourceType.SEARCH_DISCUSSIONS_SOURCE_TYPE_COMPETITION,
            "dataset": SearchDiscussionsSourceType.SEARCH_DISCUSSIONS_SOURCE_TYPE_DATASET,
        }
        if source_type in type_map:
            df.source_type = type_map[source_type]
        f.discussion_filters = df

    req.filters = f
    req.page_size = page_size
    if page_token:
        req.page_token = page_token

    try:
        resp = get_client().search.search_api_client.list_entities(req)
        return [doc.to_dict() for doc in resp.documents]
    except Exception as e:
        logger.warning(f"Search API failed: {e}")
        return []


def _scrape_discussion(discussion_id: int) -> dict:
    """HTML fallback for discussion detail."""
    try:
        resp = httpx.get(
            f"https://www.kaggle.com/discussion/{discussion_id}",
            follow_redirects=True,
            timeout=15.0,
        )
        resp.raise_for_status()
        title_match = re.search(r"<title>(.*?)</title>", resp.text)
        title = title_match.group(1) if title_match else "Unknown"
        return {"id": discussion_id, "title": title, "body": "(HTML fallback)"}
    except Exception as e:
        logger.error(f"HTML scrape failed: {e}")
        return {"id": discussion_id, "title": "Error", "body": str(e)}


def register(mcp: FastMCP) -> None:
    """Register discussion tools."""

    @mcp.tool()
    def discussions_search(query: str, page_size: int = 20) -> str:
        """Search Kaggle discussions.

        Args:
            query: Search query string.
            page_size: Number of results (max 50).
        """
        results = _search_via_sdk(query=query, page_size=page_size)
        if not results:
            return "No discussions found."
        lines = []
        for d in results:
            did = d.get("id", "?")
            title = d.get("title", "Untitled")
            votes = d.get("votes", 0)
            lines.append(f"- [{did}] **{title}** (votes: {votes})")
        return "\n".join(lines)

    @mcp.tool()
    def discussions_list(
        competition: str = "",
        dataset: str = "",
        page_size: int = 20,
    ) -> str:
        """List discussions for a competition or dataset.

        Args:
            competition: Competition slug to filter.
            dataset: Dataset ref to filter.
            page_size: Number of results (max 50).
        """
        source = ""
        query = ""
        if competition:
            source = "competition"
            query = competition
        elif dataset:
            source = "dataset"
            query = dataset

        results = _search_via_sdk(
            query=query, source_type=source, page_size=page_size
        )
        if not results:
            return "No discussions found."
        lines = []
        for d in results:
            did = d.get("id", "?")
            title = d.get("title", "Untitled")
            votes = d.get("votes", 0)
            lines.append(f"- [{did}] **{title}** (votes: {votes})")
        return "\n".join(lines)

    @mcp.tool()
    def discussion_detail(discussion_id: int) -> str:
        """Get discussion content by ID.

        Args:
            discussion_id: Numeric discussion ID.
        """
        # Get title from HTML, then search by title for full markdown
        scraped = _scrape_discussion(discussion_id)
        title = scraped.get("title", "").split("|")[0].strip()

        if title and title not in ("Unknown", "Error"):
            results = _search_via_sdk(query=title, page_size=20)
            for d in results:
                if d.get("id") == discussion_id:
                    doc = d.get("discussionDocument", {})
                    author = d.get("ownerUser", {}).get("displayName", "Unknown")
                    votes = d.get("votes", 0)
                    body = doc.get("messageMarkdown") or doc.get("messageStripped", "")
                    forum = doc.get("forumName", "")
                    t = d.get("title", title)
                    header = f"# {t}\n\n**Author:** {author} | **Votes:** {votes}"
                    if forum:
                        header += f" | **Forum:** {forum}"
                    return f"{header}\n\n{body}"

        return f"# {title}\n\nView at: https://www.kaggle.com/discussion/{discussion_id}"

    @mcp.tool()
    def discussion_comments(discussion_id: int) -> str:
        """Get comments for a discussion (HTML fallback).

        Args:
            discussion_id: Numeric discussion ID.
        """
        return f"Comments API not available. View at: https://www.kaggle.com/discussion/{discussion_id}"
