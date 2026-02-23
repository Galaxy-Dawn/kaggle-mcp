"""Kernel/Notebook tools for Kaggle MCP Server."""

from mcp.server.fastmcp import FastMCP

from .client import get_client


def register(mcp: FastMCP) -> None:
    """Register kernel tools."""

    @mcp.tool()
    def kernels_list(
        search: str = "",
        competition: str = "",
        dataset: str = "",
        sort_by: str = "",
        page: int = 1,
    ) -> str:
        """Search and list Kaggle notebooks/kernels.

        Args:
            search: Search term.
            competition: Filter by competition.
            dataset: Filter by dataset.
            sort_by: Sort order (hotness, commentCount, dateCreated, dateRun, relevance, voteCount).
            page: Page number.
        """
        from kagglesdk.kernels.services.kernels_api_service import (
            ApiListKernelsRequest,
        )

        req = ApiListKernelsRequest()
        if search:
            req.search = search
        if competition:
            req.competition = competition
        if dataset:
            req.dataset = dataset
        if sort_by:
            req.sort_by = sort_by
        req.page = page

        resp = get_client().kernels.kernels_api_client.list_kernels(req)
        kernels = resp.kernels
        if not kernels:
            return "No kernels found."
        lines = []
        for k in kernels:
            lines.append(
                f"- **{k.title}** (`{k.ref}`)\n"
                f"  Votes: {getattr(k, 'total_votes', 'N/A')} | Language: {getattr(k, 'language', 'N/A')}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def kernel_pull(user_name: str, kernel_slug: str) -> str:
        """Get a notebook's source code.

        Args:
            user_name: Kernel owner username.
            kernel_slug: Kernel slug name.
        """
        from kagglesdk.kernels.services.kernels_api_service import (
            ApiGetKernelRequest,
        )

        req = ApiGetKernelRequest()
        req.user_name = user_name
        req.kernel_slug = kernel_slug
        resp = get_client().kernels.kernels_api_client.get_kernel(req)
        meta = resp.metadata.to_dict() if resp.metadata else {}
        blob = resp.blob or "(no source)"
        return f"Metadata: {meta}\n\nSource:\n{blob}"

    @mcp.tool()
    def kernel_push(
        title: str,
        text: str,
        language: str = "python",
        kernel_type: str = "notebook",
        is_private: bool = True,
    ) -> str:
        """Push/save a notebook to Kaggle.

        Args:
            title: Notebook title.
            text: Notebook source code.
            language: Language (python, r).
            kernel_type: Type (notebook, script).
            is_private: Whether notebook is private.
        """
        from kagglesdk.kernels.services.kernels_api_service import (
            ApiSaveKernelRequest,
        )

        req = ApiSaveKernelRequest()
        req.new_title = title
        req.text = text
        req.language = language
        req.kernel_type = kernel_type
        req.is_private = is_private
        resp = get_client().kernels.kernels_api_client.save_kernel(req)
        return str(resp.to_dict())
