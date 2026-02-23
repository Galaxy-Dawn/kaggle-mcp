"""Model tools for Kaggle MCP Server."""

from mcp.server.fastmcp import FastMCP

from .client import get_client


def register(mcp: FastMCP) -> None:
    """Register model tools."""

    @mcp.tool()
    def models_list(
        search: str = "",
        owner: str = "",
        sort_by: str = "",
        page_size: int = 20,
    ) -> str:
        """Search and list Kaggle models.

        Args:
            search: Search term.
            owner: Filter by owner.
            sort_by: Sort order (hotness, downloadCount, createTime, updateTime).
            page_size: Number of results per page.
        """
        from kagglesdk.models.services.model_api_service import (
            ApiListModelsRequest,
        )

        req = ApiListModelsRequest()
        if search:
            req.search = search
        if owner:
            req.owner = owner
        if sort_by:
            req.sort_by = sort_by
        req.page_size = page_size

        resp = get_client().models.list_models(req)
        models = resp.models
        if not models:
            return "No models found."
        lines = []
        for m in models:
            lines.append(
                f"- **{getattr(m, 'title', m.model_slug)}** "
                f"(`{m.owner_slug}/{m.model_slug}`)"
            )
        return "\n".join(lines)

    @mcp.tool()
    def model_get(owner: str, model_slug: str) -> str:
        """Get detailed information about a specific model.

        Args:
            owner: Model owner username.
            model_slug: Model slug/name.
        """
        from kagglesdk.models.services.model_api_service import (
            ApiGetModelRequest,
        )

        req = ApiGetModelRequest()
        req.owner_slug = owner
        req.model_slug = model_slug
        resp = get_client().models.get_model(req)
        return str(resp.to_dict())
