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

        resp = get_client().models.model_api_client.list_models(req)
        models = resp.models
        if not models:
            return "No models found."
        lines = []
        for m in models:
            lines.append(
                f"- **{m.title or m.slug}** (`{m.ref}`)"
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
        resp = get_client().models.model_api_client.get_model(req)
        return str(resp.to_dict())

    @mcp.tool()
    def model_create(
        owner: str,
        slug: str,
        title: str,
        subtitle: str = "",
        description: str = "",
        is_private: bool = True,
    ) -> str:
        """Create a new Kaggle model.

        Args:
            owner: Owner username.
            slug: Model slug (URL-friendly identifier).
            title: Model title.
            subtitle: Optional subtitle.
            description: Optional description.
            is_private: Whether the model is private (default True).
        """
        from kagglesdk.models.types.model_api_service import ApiCreateModelRequest

        try:
            req = ApiCreateModelRequest()
            req.owner_slug = owner
            req.slug = slug
            req.title = title
            if subtitle:
                req.subtitle = subtitle
            if description:
                req.description = description
            req.is_private = is_private
            resp = get_client().models.model_api_client.create_model(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error creating model: {e}"

    @mcp.tool()
    def model_update(
        owner: str,
        model_slug: str,
        title: str = "",
        subtitle: str = "",
        description: str = "",
        is_private: bool = None,
    ) -> str:
        """Update an existing Kaggle model.

        Args:
            owner: Owner username.
            model_slug: Model slug to update.
            title: New title (leave empty to keep existing).
            subtitle: New subtitle (leave empty to keep existing).
            description: New description (leave empty to keep existing).
            is_private: New privacy setting (None to keep existing).
        """
        from kagglesdk.models.types.model_api_service import ApiUpdateModelRequest

        try:
            req = ApiUpdateModelRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            if title:
                req.title = title
            if subtitle:
                req.subtitle = subtitle
            if description:
                req.description = description
            if is_private is not None:
                req.is_private = is_private
            resp = get_client().models.model_api_client.update_model(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error updating model: {e}"

    @mcp.tool()
    def model_delete(owner: str, model_slug: str) -> str:
        """Delete a Kaggle model.

        Args:
            owner: Owner username.
            model_slug: Model slug to delete.
        """
        from kagglesdk.models.types.model_api_service import ApiDeleteModelRequest

        try:
            req = ApiDeleteModelRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            resp = get_client().models.model_api_client.delete_model(req)
            if resp.error:
                return f"Error deleting model: {resp.error}"
            return "Model deleted successfully."
        except Exception as e:
            return f"Error deleting model: {e}"

    @mcp.tool()
    def model_instances_list(owner: str, model_slug: str) -> str:
        """List all instances of a Kaggle model.

        Args:
            owner: Model owner username.
            model_slug: Model slug/name.
        """
        from kagglesdk.models.types.model_api_service import ApiListModelInstancesRequest

        try:
            req = ApiListModelInstancesRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            resp = get_client().models.model_api_client.list_model_instances(req)
            instances = resp.instances
            if not instances:
                return "No instances found."
            lines = []
            for inst in instances:
                lines.append(
                    f"- **{inst.framework}** / `{inst.overview or inst.id}`"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing model instances: {e}"

    @mcp.tool()
    def model_instance_get(
        owner: str,
        model_slug: str,
        framework: str,
        instance_slug: str,
    ) -> str:
        """Get details of a specific model instance.

        Args:
            owner: Model owner username.
            model_slug: Model slug/name.
            framework: Framework name (e.g. 'tensorflow2', 'pytorch', 'jax').
            instance_slug: Instance slug identifier.
        """
        from kagglesdk.models.types.model_api_service import ApiGetModelInstanceRequest

        try:
            req = ApiGetModelInstanceRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            req.framework = framework
            req.instance_slug = instance_slug
            resp = get_client().models.model_api_client.get_model_instance(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error getting model instance: {e}"

    @mcp.tool()
    def model_instance_create(
        owner: str,
        model_slug: str,
        framework: str,
        instance_slug: str,
        overview: str = "",
        usage: str = "",
        license_name: str = "Apache 2.0",
        is_private: bool = True,
    ) -> str:
        """Create a new instance for a Kaggle model.

        Args:
            owner: Model owner username.
            model_slug: Model slug/name.
            framework: Framework name (e.g. 'tensorflow2', 'pytorch', 'jax').
            instance_slug: Slug for the new instance.
            overview: Optional overview text.
            usage: Optional usage instructions.
            license_name: License name (default 'Apache 2.0').
            is_private: Whether the instance is private (default True).
        """
        from kagglesdk.models.types.model_api_service import (
            ApiCreateModelInstanceRequest,
            ApiCreateModelInstanceRequestBody,
        )

        try:
            body = ApiCreateModelInstanceRequestBody()
            body.instance_slug = instance_slug
            body.framework = framework
            if overview:
                body.overview = overview
            if usage:
                body.usage = usage
            body.license_name = license_name
            req = ApiCreateModelInstanceRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            req.body = body
            resp = get_client().models.model_api_client.create_model_instance(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error creating model instance: {e}"

    @mcp.tool()
    def model_instance_versions(
        owner: str,
        model_slug: str,
        framework: str,
        instance_slug: str,
    ) -> str:
        """List all versions of a model instance.

        Args:
            owner: Model owner username.
            model_slug: Model slug/name.
            framework: Framework name (e.g. 'tensorflow2', 'pytorch', 'jax').
            instance_slug: Instance slug identifier.
        """
        from kagglesdk.models.types.model_api_service import ApiListModelInstanceVersionsRequest

        try:
            req = ApiListModelInstanceVersionsRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            req.framework = framework
            req.instance_slug = instance_slug
            resp = get_client().models.model_api_client.list_model_instance_versions(req)
            version_list = resp.version_list
            if not version_list:
                return "No versions found."
            return str(version_list.to_dict())
        except Exception as e:
            return f"Error listing model instance versions: {e}"

    @mcp.tool()
    def model_instance_version_create(
        owner: str,
        model_slug: str,
        framework: str,
        instance_slug: str,
        version_notes: str = "",
    ) -> str:
        """Create a new version for a model instance.

        Args:
            owner: Model owner username.
            model_slug: Model slug/name.
            framework: Framework name (e.g. 'tensorflow2', 'pytorch', 'jax').
            instance_slug: Instance slug identifier.
            version_notes: Optional notes for this version.
        """
        from kagglesdk.models.types.model_api_service import (
            ApiCreateModelInstanceVersionRequest,
            ApiCreateModelInstanceVersionRequestBody,
        )

        try:
            body = ApiCreateModelInstanceVersionRequestBody()
            if version_notes:
                body.version_notes = version_notes
            req = ApiCreateModelInstanceVersionRequest()
            req.owner_slug = owner
            req.model_slug = model_slug
            req.framework = framework
            req.instance_slug = instance_slug
            req.body = body
            resp = get_client().models.model_api_client.create_model_instance_version(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error creating model instance version: {e}"
