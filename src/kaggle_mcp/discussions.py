"""Discussion tools for Kaggle MCP Server."""

import logging

from mcp.server.fastmcp import FastMCP

from .client import get_client

logger = logging.getLogger(__name__)

# Maps user-facing sort_by strings to ListSearchContentOrderBy enum values
_SORT_MAP = {
    "hotness": "LIST_SEARCH_CONTENT_ORDER_BY_HOTNESS",
    "votes": "LIST_SEARCH_CONTENT_ORDER_BY_VOTES",
    "comments": "LIST_SEARCH_CONTENT_ORDER_BY_TOTAL_COMMENTS",
    "created": "LIST_SEARCH_CONTENT_ORDER_BY_DATE_CREATED",
    "updated": "LIST_SEARCH_CONTENT_ORDER_BY_DATE_UPDATED",
}

# Maps user-facing source_type strings to SearchDiscussionsSourceType enum values
_SOURCE_MAP = {
    "competition": "SEARCH_DISCUSSIONS_SOURCE_TYPE_COMPETITION",
    "dataset": "SEARCH_DISCUSSIONS_SOURCE_TYPE_DATASET",
    "kernel": "SEARCH_DISCUSSIONS_SOURCE_TYPE_KERNEL",
    "site_forum": "SEARCH_DISCUSSIONS_SOURCE_TYPE_SITE_FORUM",
    "competition_solution": "SEARCH_DISCUSSIONS_SOURCE_TYPE_COMPETITION_SOLUTION",
    "model": "SEARCH_DISCUSSIONS_SOURCE_TYPE_MODEL",
    "write_up": "SEARCH_DISCUSSIONS_SOURCE_TYPE_WRITE_UP",
    "learn_track": "SEARCH_DISCUSSIONS_SOURCE_TYPE_LEARN_TRACK",
    "benchmark": "SEARCH_DISCUSSIONS_SOURCE_TYPE_BENCHMARK",
    "benchmark_task": "SEARCH_DISCUSSIONS_SOURCE_TYPE_BENCHMARK_TASK",
}

# Maps user-facing write_up_type strings to WriteUpType enum values
_WRITEUP_TYPE_MAP = {
    "knowledge": "KNOWLEDGE",
    "competition_solution": "COMPETITION_SOLUTION",
    "hackathon": "HACKATHON_PROJECT",
    "personal_project": "PERSONAL_PROJECT",
    "forum_topic": "FORUM_TOPIC",
    "blog": "BLOG",
}


def _fmt_doc(d: dict) -> str:
    """Format a single discussion document dict as a Markdown list item."""
    did = d.get("id", "?")
    title = d.get("title", "Untitled")
    votes = d.get("votes", 0)
    author = d.get("ownerUser", {}).get("displayName", "")
    author_str = f" | by {author}" if author else ""
    updated = d.get("updateTime", "") or d.get("createTime", "")
    date_str = f" | {updated[:10]}" if updated else ""
    return f"- [{did}] **{title}** (votes: {votes}{author_str}{date_str})"


def _search_via_sdk(
    query: str = "",
    source_type: str = "",
    sort_by: str = "",
    document_type: str = "TOPIC",
    write_up_types: list[str] | None = None,
    list_type: str = "",
    page_size: int = 20,
    discussions_order_by: str = "",
) -> list[dict]:
    """Search discussions via kagglesdk search API.

    Args:
        query: Free-text search query.
        source_type: Key from _SOURCE_MAP or empty string.
        sort_by: Key from _SORT_MAP or empty string.
        document_type: DocumentType enum name string (e.g. "TOPIC", "COMMENT").
        write_up_types: List of WriteUpType enum name strings.
        list_type: "your_work" to filter to current user's content.
        page_size: Max results to return.

    Returns:
        List of document dicts from the API response.
    """
    from kagglesdk.search.services.search_api_service import ListEntitiesRequest
    from kagglesdk.search.types.search_api_service import (
        ApiListType,
        ApiSearchDiscussionsFilters,
        ListEntitiesFilters,
    )
    from kagglesdk.search.types.search_enums import DocumentType, ListSearchContentOrderBy

    req = ListEntitiesRequest()
    f = ListEntitiesFilters()

    doc_type_enum = getattr(DocumentType, document_type, DocumentType.TOPIC)
    f.document_types = [doc_type_enum]

    if query:
        f.query = query

    if list_type == "your_work":
        f.list_type = ApiListType.API_LIST_TYPE_YOUR_WORK

    # Build discussion-specific filters
    df = ApiSearchDiscussionsFilters()
    needs_df = False

    if source_type and source_type in _SOURCE_MAP:
        from kagglesdk.discussions.types.search_discussions import SearchDiscussionsSourceType
        enum_name = _SOURCE_MAP[source_type]
        df.source_type = getattr(SearchDiscussionsSourceType, enum_name)
        needs_df = True

    if write_up_types:
        from kagglesdk.discussions.types.writeup_enums import WriteUpType
        wt_list = []
        for wt in write_up_types:
            enum_name = _WRITEUP_TYPE_MAP.get(wt, wt.upper())
            val = getattr(WriteUpType, enum_name, None)
            if val is not None:
                wt_list.append(val)
        if wt_list:
            df.write_up_types = wt_list
            needs_df = True

    if needs_df:
        f.discussion_filters = df

    req.filters = f
    req.page_size = page_size

    if sort_by and sort_by in _SORT_MAP:
        enum_name = _SORT_MAP[sort_by]
        req.canonical_order_by = getattr(ListSearchContentOrderBy, enum_name)

    if discussions_order_by:
        from kagglesdk.discussions.types.search_discussions import SearchDiscussionsOrderBy
        order_enum = getattr(SearchDiscussionsOrderBy, discussions_order_by, None)
        if order_enum is not None:
            req.discussions_order_by = order_enum

    try:
        resp = get_client().search.search_api_client.list_entities(req)
        return [doc.to_dict() for doc in resp.documents]
    except Exception as e:
        logger.warning("Search API failed: %s", e)
        return []


def register(mcp: FastMCP) -> None:
    """Register discussion tools."""

    @mcp.tool()
    def discussions_search(
        query: str,
        sort_by: str = "",
        source_type: str = "",
        page_size: int = 20,
    ) -> str:
        """Search Kaggle discussions.

        Args:
            query: Search query string.
            sort_by: Sort order: hotness, votes, comments, created, updated.
            source_type: Filter by source: competition, dataset, kernel, site_forum,
                competition_solution, model, write_up, learn_track, benchmark, benchmark_task.
            page_size: Number of results (max 50).
        """
        try:
            results = _search_via_sdk(
                query=query, sort_by=sort_by, source_type=source_type, page_size=page_size
            )
            if not results:
                return "No discussions found."
            return "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error searching discussions: {e}"

    @mcp.tool()
    def discussions_list(
        competition: str = "",
        dataset: str = "",
        page_size: int = 20,
        since_hours: int = 0,
        new_only: bool = False,
    ) -> str:
        """List discussions for a competition or dataset.

        Args:
            competition: Competition slug to filter.
            dataset: Dataset ref to filter.
            page_size: Number of results (max 50).
            since_hours: If > 0, only return discussions within the last N hours.
                         Fetches up to 100 results and filters client-side.
            new_only: If True, filter by createTime (newly posted threads only).
                      If False (default), filter by updateTime (includes threads with new replies).
        """
        from datetime import datetime, timezone, timedelta

        try:
            source = ""
            query = ""
            if competition:
                source = "competition"
                query = competition
            elif dataset:
                source = "dataset"
                query = dataset

            fetch_size = max(page_size, 100) if since_hours > 0 else page_size
            if since_hours > 0:
                order_by = "" if new_only else "SEARCH_DISCUSSIONS_ORDER_BY_LAST_TOPIC_COMMENT_DATE"
                sort_by = "created" if new_only else ""
            else:
                order_by = ""
                sort_by = ""

            results = _search_via_sdk(
                query=query,
                source_type=source,
                page_size=fetch_size,
                discussions_order_by=order_by,
                sort_by=sort_by,
            )

            if since_hours > 0:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
                time_key = "createTime" if new_only else "updateTime"
                filtered = []
                for d in results:
                    ts = d.get(time_key) or d.get("createTime", "")
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if dt >= cutoff:
                                filtered.append(d)
                        except ValueError:
                            pass
                results = filtered[:page_size]

            if not results:
                label = "新发布" if new_only else "活跃"
                suffix = f" (最近 {since_hours}h {label})" if since_hours > 0 else ""
                return f"No discussions found{suffix}."
            return "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error listing discussions: {e}"

    @mcp.tool()
    def discussion_detail(discussion_id: int, competition: str = "") -> str:
        """Get discussion content by ID.

        Args:
            discussion_id: Numeric discussion ID.
            competition: Competition slug to narrow the search (recommended for accuracy).
        """
        def _find_in_results(results: list) -> str | None:
            for d in results:
                if d.get("id") == discussion_id:
                    doc = d.get("discussionDocument", {})
                    author = d.get("ownerUser", {}).get("displayName", "Unknown")
                    votes = d.get("votes", 0)
                    body = doc.get("messageMarkdown") or doc.get("messageStripped", "")
                    forum = doc.get("forumName", "")
                    title = d.get("title", f"Discussion {discussion_id}")
                    header = f"# {title}\n\n**Author:** {author} | **Votes:** {votes}"
                    if forum:
                        header += f" | **Forum:** {forum}"
                    return f"{header}\n\n{body}" if body else header
            return None

        try:
            # Strategy 1: search within competition context (most reliable)
            if competition:
                results = _search_via_sdk(
                    query=competition,
                    source_type="competition",
                    page_size=50,
                )
                found = _find_in_results(results)
                if found:
                    return found

            # Strategy 2: broader search across all source types
            for source in ["competition", "dataset", "kernel", ""]:
                results = _search_via_sdk(query=competition or "", source_type=source, page_size=50)
                found = _find_in_results(results)
                if found:
                    return found

            return (
                f"Discussion {discussion_id} not found via search. "
                f"Tip: pass competition='<slug>' for better results. "
                f"View at: https://www.kaggle.com/discussion/{discussion_id}"
            )
        except Exception as e:
            return f"Error fetching discussion {discussion_id}: {e}"

    @mcp.tool()
    def discussion_comments(discussion_id: int, page_size: int = 20) -> str:
        """Get comments for a discussion.

        Args:
            discussion_id: Numeric discussion ID.
            page_size: Number of comments to return (max 50).
        """
        try:
            results = _search_via_sdk(
                query=str(discussion_id),
                document_type="COMMENT",
                page_size=page_size,
            )
            if not results:
                return (
                    f"No comments found. "
                    f"View at: https://www.kaggle.com/discussion/{discussion_id}"
                )
            lines = [f"## Comments for discussion {discussion_id}\n"]
            for d in results:
                doc = d.get("discussionDocument", {})
                author = d.get("ownerUser", {}).get("displayName", "Unknown")
                body = doc.get("messageMarkdown") or doc.get("messageStripped", "")
                votes = d.get("votes", 0)
                lines.append(f"**{author}** (votes: {votes})\n{body}\n---")
            return "\n".join(lines)
        except Exception as e:
            return f"Error fetching comments for discussion {discussion_id}: {e}"

    @mcp.tool()
    def discussion_comments_search(query: str, page_size: int = 20) -> str:
        """Search comments across all Kaggle discussions.

        Args:
            query: Search query string.
            page_size: Number of results (max 50).
        """
        try:
            results = _search_via_sdk(
                query=query, document_type="COMMENT", page_size=page_size
            )
            if not results:
                return "No comments found."
            lines = [f"## Comment search results for: {query}\n"]
            for d in results:
                doc = d.get("discussionDocument", {})
                author = d.get("ownerUser", {}).get("displayName", "Unknown")
                body = doc.get("messageMarkdown") or doc.get("messageStripped", "")
                votes = d.get("votes", 0)
                did = d.get("id", "?")
                lines.append(f"**[{did}] {author}** (votes: {votes})\n{body}\n---")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching comments: {e}"

    @mcp.tool()
    def discussions_by_source(
        source_type: str,
        query: str = "",
        sort_by: str = "hotness",
        page_size: int = 20,
    ) -> str:
        """Browse discussions by source type.

        Args:
            source_type: One of: competition, dataset, kernel, site_forum,
                competition_solution, model, write_up, learn_track, benchmark, benchmark_task.
            query: Optional search query to filter results.
            sort_by: Sort order: hotness, votes, comments, created, updated.
            page_size: Number of results (max 50).
        """
        try:
            if source_type not in _SOURCE_MAP:
                valid = ", ".join(_SOURCE_MAP.keys())
                return f"Invalid source_type '{source_type}'. Valid values: {valid}"
            results = _search_via_sdk(
                query=query,
                source_type=source_type,
                sort_by=sort_by,
                page_size=page_size,
            )
            if not results:
                return f"No discussions found for source_type='{source_type}'."
            header = f"## Discussions: {source_type}"
            if query:
                header += f" | query: {query}"
            return header + "\n\n" + "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error browsing discussions by source: {e}"

    @mcp.tool()
    def discussions_solutions(
        competition: str = "",
        sort_by: str = "votes",
        page_size: int = 20,
    ) -> str:
        """Browse competition solution write-ups.

        Args:
            competition: Optional competition slug to filter solutions.
            sort_by: Sort order: hotness, votes, comments, created, updated.
            page_size: Number of results (max 50).
        """
        try:
            results = _search_via_sdk(
                query=competition,
                source_type="competition_solution",
                sort_by=sort_by,
                write_up_types=["competition_solution"],
                page_size=page_size,
            )
            if not results:
                return "No competition solutions found."
            header = "## Competition Solutions"
            if competition:
                header += f": {competition}"
            return header + "\n\n" + "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error fetching competition solutions: {e}"

    @mcp.tool()
    def discussions_writeups(
        write_up_type: str = "knowledge",
        query: str = "",
        page_size: int = 20,
    ) -> str:
        """Browse Kaggle write-ups by type.

        Args:
            write_up_type: One of: knowledge, competition_solution, hackathon,
                personal_project, forum_topic, blog.
            query: Optional search query to filter results.
            page_size: Number of results (max 50).
        """
        try:
            if write_up_type not in _WRITEUP_TYPE_MAP:
                valid = ", ".join(_WRITEUP_TYPE_MAP.keys())
                return f"Invalid write_up_type '{write_up_type}'. Valid values: {valid}"
            results = _search_via_sdk(
                query=query,
                source_type="write_up",
                write_up_types=[write_up_type],
                sort_by="votes",
                page_size=page_size,
            )
            if not results:
                return f"No write-ups found for type='{write_up_type}'."
            header = f"## Write-ups: {write_up_type}"
            if query:
                header += f" | query: {query}"
            return header + "\n\n" + "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error fetching write-ups: {e}"

    @mcp.tool()
    def discussions_trending(
        source_type: str = "",
        page_size: int = 20,
    ) -> str:
        """Browse trending discussions sorted by hotness.

        Args:
            source_type: Optional filter: competition, dataset, kernel, site_forum,
                competition_solution, model, write_up, learn_track, benchmark, benchmark_task.
            page_size: Number of results (max 50).
        """
        try:
            if source_type and source_type not in _SOURCE_MAP:
                valid = ", ".join(_SOURCE_MAP.keys())
                return f"Invalid source_type '{source_type}'. Valid values: {valid}"
            results = _search_via_sdk(
                source_type=source_type,
                sort_by="hotness",
                page_size=page_size,
            )
            if not results:
                return "No trending discussions found."
            header = "## Trending Discussions"
            if source_type:
                header += f": {source_type}"
            return header + "\n\n" + "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error fetching trending discussions: {e}"

    @mcp.tool()
    def discussions_my(page_size: int = 20) -> str:
        """List the current user's discussions.

        Args:
            page_size: Number of results (max 50).
        """
        try:
            results = _search_via_sdk(list_type="your_work", page_size=page_size)
            if not results:
                return "No discussions found for your account."
            return "## My Discussions\n\n" + "\n".join(_fmt_doc(d) for d in results)
        except Exception as e:
            return f"Error fetching your discussions: {e}"
