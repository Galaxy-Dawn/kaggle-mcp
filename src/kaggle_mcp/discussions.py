"""Discussion tools for Kaggle MCP Server (hidden API + HTML fallback)."""

import json
import logging
import os
import re

import httpx
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

KAGGLE_BASE = "https://www.kaggle.com/api/v1"
_http: httpx.Client | None = None


def _get_http() -> httpx.Client:
    """Get httpx client with Kaggle basic auth."""
    global _http
    if _http is None:
        creds_path = os.path.expanduser(
            os.environ.get("KAGGLE_CONFIG_DIR", "~/.kaggle") + "/kaggle.json"
        )
        with open(creds_path) as f:
            creds = json.load(f)
        _http = httpx.Client(
            base_url=KAGGLE_BASE,
            auth=(creds["username"], creds["key"]),
            timeout=30.0,
        )
    return _http


def _search_discussions(query: str, page: int = 1, group: str = "") -> list[dict]:
    """Search discussions via Kaggle API."""
    http = _get_http()
    params: dict = {"page": page, "sortBy": "relevance"}
    if query:
        params["search"] = query
    if group:
        params["group"] = group
    try:
        resp = http.get("/discussions/list", params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning(f"Discussion list API failed: {e}")
        return []


def _get_discussion_by_id(discussion_id: int) -> dict:
    """Get discussion detail by ID, with HTML fallback."""
    http = _get_http()
    try:
        resp = http.get(f"/discussions/{discussion_id}")
        resp.raise_for_status()
        return resp.json()
    except Exception:
        logger.warning(f"Discussion API failed for {discussion_id}, trying HTML")
        return _scrape_discussion(discussion_id)


def _scrape_discussion(discussion_id: int) -> dict:
    """HTML fallback for discussion detail."""
    try:
        resp = httpx.get(
            f"https://www.kaggle.com/discussions/{discussion_id}",
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


def _get_comments(discussion_id: int) -> list[dict]:
    """Get comments for a discussion."""
    http = _get_http()
    try:
        resp = http.get(f"/discussions/{discussion_id}/comments")
        resp.raise_for_status()
        return resp.json()
    except Exception:
        logger.warning("Comments API failed, returning empty")
        return []


def register(mcp: FastMCP) -> None:
    """Register discussion tools."""

    @mcp.tool()
    def discussions_search(query: str, page: int = 1) -> str:
        """Search Kaggle discussions.

        Args:
            query: Search query string.
            page: Page number.
        """
        results = _search_discussions(query, page)
        if not results:
            return "No discussions found."
        lines = []
        for d in results:
            did = d.get("id", "?")
            title = d.get("title", "Untitled")
            votes = d.get("voteCount", d.get("votes", 0))
            lines.append(f"- [{did}] **{title}** (votes: {votes})")
        return "\n".join(lines)

    @mcp.tool()
    def discussions_list(
        competition: str = "",
        dataset: str = "",
        page: int = 1,
    ) -> str:
        """List discussions for a competition or dataset.

        Args:
            competition: Competition slug to filter.
            dataset: Dataset ref to filter.
            page: Page number.
        """
        group = ""
        if competition:
            group = f"competition/{competition}"
        elif dataset:
            group = f"dataset/{dataset}"
        results = _search_discussions("", page, group)
        if not results:
            return "No discussions found."
        lines = []
        for d in results:
            did = d.get("id", "?")
            title = d.get("title", "Untitled")
            comments = d.get("commentCount", d.get("comments", 0))
            lines.append(f"- [{did}] **{title}** ({comments} comments)")
        return "\n".join(lines)

    @mcp.tool()
    def discussion_detail(discussion_id: int) -> str:
        """Get discussion content by ID.

        Args:
            discussion_id: Numeric discussion ID.
        """
        d = _get_discussion_by_id(discussion_id)
        title = d.get("title", "Unknown")
        body = d.get("body", d.get("content", "No content"))
        author = d.get("author", d.get("userName", "Unknown"))
        return f"# {title}\nAuthor: {author}\n\n{body}"

    @mcp.tool()
    def discussion_comments(discussion_id: int) -> str:
        """Get comments for a discussion.

        Args:
            discussion_id: Numeric discussion ID.
        """
        comments = _get_comments(discussion_id)
        if not comments:
            return "No comments found."
        lines = []
        for c in comments:
            author = c.get("author", c.get("userName", "?"))
            body = c.get("body", c.get("content", ""))
            votes = c.get("voteCount", 0)
            lines.append(f"**{author}** (votes: {votes}):\n{body}\n")
        return "\n---\n".join(lines)
