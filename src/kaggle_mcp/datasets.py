"""Dataset tools for Kaggle MCP Server."""

from mcp.server.fastmcp import FastMCP

from .client import get_client


def register(mcp: FastMCP) -> None:
    """Register dataset tools."""

    @mcp.tool()
    def datasets_list(
        search: str = "",
        sort_by: str = "",
        file_type: str = "",
        page: int = 1,
    ) -> str:
        """Search and list Kaggle datasets.

        Args:
            search: Search term.
            sort_by: Sort order (hottest, votes, updated, active).
            file_type: Filter by file type (csv, json, sqlite, etc).
            page: Page number.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiListDatasetsRequest,
        )

        req = ApiListDatasetsRequest()
        if search:
            req.search = search
        if sort_by:
            req.sort_by = sort_by
        if file_type:
            req.file_type = file_type
        req.page = page

        resp = get_client().datasets.dataset_api_client.list_datasets(req)
        ds = resp.datasets
        if not ds:
            return "No datasets found."
        lines = []
        for d in ds:
            lines.append(
                f"- **{d.title}** (`{d.ref}`)\n"
                f"  Size: {d.total_bytes} bytes | Downloads: {d.download_count}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def dataset_files(owner: str, dataset_slug: str) -> str:
        """List files in a dataset.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiListDatasetFilesRequest,
        )

        req = ApiListDatasetFilesRequest()
        req.owner_slug = owner
        req.dataset_slug = dataset_slug
        resp = get_client().datasets.dataset_api_client.list_dataset_files(req)
        files = resp.files
        if not files:
            return "No files found."
        lines = [f"- {f.name} ({getattr(f, 'total_bytes', 'N/A')} bytes)" for f in files]
        return "\n".join(lines)

    @mcp.tool()
    def dataset_download(owner: str, dataset_slug: str, file_name: str = "") -> str:
        """Download dataset files. Returns download URL.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
            file_name: Specific file. Empty for all.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiDownloadDatasetRequest,
        )

        req = ApiDownloadDatasetRequest()
        req.owner_slug = owner
        req.dataset_slug = dataset_slug
        if file_name:
            req.file_name = file_name
        resp = get_client().datasets.dataset_api_client.download_dataset(req)
        return f"Download URL: {getattr(resp, 'url', str(resp))}"

    @mcp.tool()
    def dataset_metadata(owner: str, dataset_slug: str) -> str:
        """Get dataset metadata.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiGetDatasetMetadataRequest,
        )

        req = ApiGetDatasetMetadataRequest()
        req.owner_slug = owner
        req.dataset_slug = dataset_slug
        resp = get_client().datasets.dataset_api_client.get_dataset_metadata(req)
        return str(resp.to_dict())

    @mcp.tool()
    def dataset_create(
        owner: str,
        slug: str,
        title: str,
        license_name: str = "CC0-1.0",
        is_private: bool = True,
    ) -> str:
        """Create a new dataset.

        Args:
            owner: Owner username.
            slug: Dataset slug.
            title: Dataset title.
            license_name: License (e.g. CC0-1.0, CC-BY-SA-4.0).
            is_private: Whether dataset is private.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiCreateDatasetRequest,
        )

        req = ApiCreateDatasetRequest()
        req.owner_slug = owner
        req.slug = slug
        req.title = title
        req.license_name = license_name
        req.is_private = is_private
        resp = get_client().datasets.dataset_api_client.create_dataset(req)
        return str(resp.to_dict())
