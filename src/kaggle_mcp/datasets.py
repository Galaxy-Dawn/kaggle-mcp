"""Dataset tools for Kaggle MCP Server."""

import requests
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
        return f"Download URL: {resp.url}"

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
        file_tokens: str = "",
        license_name: str = "CC0-1.0",
        is_private: bool = True,
    ) -> str:
        """Create a new dataset. Use file_upload first to get file tokens.

        Args:
            owner: Owner username.
            slug: Dataset slug.
            title: Dataset title.
            file_tokens: Comma-separated file tokens from file_upload.
            license_name: License (e.g. CC0-1.0, CC-BY-SA-4.0).
            is_private: Whether dataset is private.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiCreateDatasetRequest,
        )
        from kagglesdk.datasets.types.dataset_api_service import ApiDatasetNewFile

        req = ApiCreateDatasetRequest()
        req.owner_slug = owner
        req.slug = slug
        req.title = title
        req.license_name = license_name
        req.is_private = is_private
        if file_tokens:
            files = []
            for t in file_tokens.split(","):
                f = ApiDatasetNewFile()
                f.token = t.strip()
                files.append(f)
            req.files = files
        resp = get_client().datasets.dataset_api_client.create_dataset(req)
        return str(resp.to_dict())

    @mcp.tool()
    def file_upload(file_name: str, content: str) -> str:
        """Upload a file to Kaggle and get a token for dataset_create.

        Args:
            file_name: File name (e.g. 'data.csv', 'config.json').
            content: File content as text.
        """
        from kagglesdk.datasets.services.dataset_api_service import (
            ApiUploadDatasetFileRequest,
        )

        data = content.encode("utf-8")
        c = get_client()
        req = ApiUploadDatasetFileRequest()
        req.file_name = file_name
        req.content_length = len(data)
        req.last_modified_epoch_seconds = 0
        resp = c.datasets.dataset_api_client.upload_dataset_file(req)

        requests.put(
            resp.create_url,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
        )
        return f"Token: {resp.token}"

    @mcp.tool()
    def dataset_get(owner: str, dataset_slug: str) -> str:
        """Get full dataset info.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
        """
        try:
            from kagglesdk.datasets.services.dataset_api_service import (
                ApiGetDatasetRequest,
            )

            req = ApiGetDatasetRequest()
            req.owner_slug = owner
            req.dataset_slug = dataset_slug
            resp = get_client().datasets.dataset_api_client.get_dataset(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error fetching dataset info: {e}"

    @mcp.tool()
    def dataset_create_version(
        owner: str,
        dataset_slug: str,
        version_notes: str,
        file_tokens: str = "",
    ) -> str:
        """Create a new version of an existing dataset.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
            version_notes: Notes describing this version.
            file_tokens: Comma-separated file tokens from file_upload.
        """
        try:
            from kagglesdk.datasets.services.dataset_api_service import (
                ApiCreateDatasetVersionRequest,
            )
            from kagglesdk.datasets.types.dataset_api_service import (
                ApiCreateDatasetVersionRequestBody,
                ApiDatasetNewFile,
            )

            body = ApiCreateDatasetVersionRequestBody()
            body.version_notes = version_notes
            if file_tokens:
                files = []
                for t in file_tokens.split(","):
                    f = ApiDatasetNewFile()
                    f.token = t.strip()
                    files.append(f)
                body.files = files

            req = ApiCreateDatasetVersionRequest()
            req.owner_slug = owner
            req.dataset_slug = dataset_slug
            req.body = body
            resp = get_client().datasets.dataset_api_client.create_dataset_version(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error creating dataset version: {e}"

    @mcp.tool()
    def dataset_update_metadata(
        owner: str,
        dataset_slug: str,
        title: str = "",
        description: str = "",
        license_name: str = "",
    ) -> str:
        """Update dataset metadata (title, description, license).

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
            title: New title (leave empty to keep current).
            description: New description (leave empty to keep current).
            license_name: New license name (leave empty to keep current).
        """
        try:
            from kagglesdk.datasets.services.dataset_api_service import (
                ApiUpdateDatasetMetadataRequest,
            )
            from kagglesdk.datasets.types.dataset_types import (
                DatasetSettings,
                SettingsLicense,
            )

            settings = DatasetSettings()
            if title:
                settings.title = title
            if description:
                settings.description = description
            if license_name:
                lic = SettingsLicense()
                lic.name = license_name
                settings.licenses = [lic]

            req = ApiUpdateDatasetMetadataRequest()
            req.owner_slug = owner
            req.dataset_slug = dataset_slug
            req.settings = settings
            resp = get_client().datasets.dataset_api_client.update_dataset_metadata(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error updating dataset metadata: {e}"

    @mcp.tool()
    def dataset_delete(owner: str, dataset_slug: str) -> str:
        """Delete a dataset.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
        """
        try:
            from kagglesdk.datasets.services.dataset_api_service import (
                ApiDeleteDatasetRequest,
            )

            req = ApiDeleteDatasetRequest()
            req.owner_slug = owner
            req.dataset_slug = dataset_slug
            resp = get_client().datasets.dataset_api_client.delete_dataset(req)
            if resp.error:
                return f"Error deleting dataset: {resp.error}"
            return "Dataset deleted successfully."
        except Exception as e:
            return f"Error deleting dataset: {e}"

    @mcp.tool()
    def dataset_download_file(owner: str, dataset_slug: str, file_name: str) -> str:
        """Download a single file from a dataset. Returns download URL.

        Args:
            owner: Dataset owner username.
            dataset_slug: Dataset slug name.
            file_name: Name of the specific file to download.
        """
        try:
            from kagglesdk.datasets.services.dataset_api_service import (
                ApiDownloadDatasetRequest,
            )

            req = ApiDownloadDatasetRequest()
            req.owner_slug = owner
            req.dataset_slug = dataset_slug
            req.file_name = file_name
            resp = get_client().datasets.dataset_api_client.download_dataset(req)
            return f"Download URL: {resp.url}"
        except Exception as e:
            return f"Error downloading file: {e}"
