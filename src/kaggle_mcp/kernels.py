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

        from kagglesdk.kernels.types.kernels_api_service import KernelsListSortType

        _sort_map = {
            "hotness": KernelsListSortType.HOTNESS,
            "commentCount": KernelsListSortType.COMMENT_COUNT,
            "dateCreated": KernelsListSortType.DATE_CREATED,
            "dateRun": KernelsListSortType.DATE_RUN,
            "relevance": KernelsListSortType.RELEVANCE,
            "voteCount": KernelsListSortType.VOTE_COUNT,
        }

        req = ApiListKernelsRequest()
        if search:
            req.search = search
        if competition:
            req.competition = competition
        if dataset:
            req.dataset = dataset
        if sort_by and sort_by in _sort_map:
            req.sort_by = _sort_map[sort_by]
        req.page = page

        try:
            resp = get_client().kernels.kernels_api_client.list_kernels(req)
        except Exception as e:
            return f"Error listing kernels: {e}"
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
        source = resp.blob.source if resp.blob else "(no source)"
        return f"Metadata: {meta}\n\nSource:\n{source}"

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

    @mcp.tool()
    def kernel_output(user_name: str, kernel_slug: str) -> str:
        """Download competition data files. Returns download URL.

        Args:
            user_name: Kernel owner username.
            kernel_slug: Kernel slug name.
        """
        from kagglesdk.kernels.types.kernels_api_service import (
            ApiDownloadKernelOutputRequest,
        )

        try:
            req = ApiDownloadKernelOutputRequest()
            req.owner_slug = user_name
            req.kernel_slug = kernel_slug
            resp = get_client().kernels.kernels_api_client.download_kernel_output(req)
            url = getattr(resp, "url", None) or str(resp)
            return f"Download URL: {url}"
        except Exception as e:
            return f"Error downloading kernel output: {e}"

    @mcp.tool()
    def kernel_session_create(user_name: str, kernel_slug: str) -> str:
        """Create an interactive kernel session.

        Args:
            user_name: Kernel owner username.
            kernel_slug: Kernel slug name.
        """
        from kagglesdk.kernels.types.kernels_api_service import (
            ApiCreateKernelSessionRequest,
        )

        try:
            req = ApiCreateKernelSessionRequest()
            req.slug = f"{user_name}/{kernel_slug}"
            resp = get_client().kernels.kernels_api_client.create_kernel_session(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error creating kernel session: {e}"

    @mcp.tool()
    def kernel_session_status(user_name: str, kernel_slug: str) -> str:
        """Get status of a kernel session.

        Args:
            user_name: Kernel owner username.
            kernel_slug: Kernel slug name.
        """
        from kagglesdk.kernels.types.kernels_api_service import (
            ApiGetKernelSessionStatusRequest,
        )

        try:
            req = ApiGetKernelSessionStatusRequest()
            req.user_name = user_name
            req.kernel_slug = kernel_slug
            resp = get_client().kernels.kernels_api_client.get_kernel_session_status(req)
            status = getattr(resp.status, "name", str(resp.status))
            failure = resp.failure_message
            lines = [f"**Status**: {status}"]
            if failure:
                lines.append(f"**Failure message**: {failure}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error fetching session status: {e}"

    @mcp.tool()
    def kernel_session_output(user_name: str, kernel_slug: str) -> str:
        """List output files from a kernel session.

        Args:
            user_name: Kernel owner username.
            kernel_slug: Kernel slug name.
        """
        from kagglesdk.kernels.types.kernels_api_service import (
            ApiListKernelSessionOutputRequest,
        )

        try:
            req = ApiListKernelSessionOutputRequest()
            req.user_name = user_name
            req.kernel_slug = kernel_slug
            resp = get_client().kernels.kernels_api_client.list_kernel_session_output(req)
            files = resp.files or []
            if not files:
                return "No output files found."
            lines = [f"**Output files** for `{user_name}/{kernel_slug}`:"]
            for f in files:
                name = getattr(f, "file_name", None) or getattr(f, "name", "unknown")
                url = getattr(f, "url", "N/A")
                lines.append(f"- `{name}` — {url}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing session output: {e}"

    @mcp.tool()
    def kernel_session_cancel(user_name: str, kernel_slug: str) -> str:
        """Cancel a running kernel session.

        Args:
            user_name: Kernel owner username.
            kernel_slug: Kernel slug name.
        """
        from kagglesdk.kernels.types.kernels_api_service import (
            ApiCancelKernelSessionRequest,
        )

        try:
            req = ApiCancelKernelSessionRequest()
            # Cancel requires kernel_session_id; fetch status first to resolve it
            from kagglesdk.kernels.types.kernels_api_service import (
                ApiGetKernelSessionStatusRequest,
            )
            status_req = ApiGetKernelSessionStatusRequest()
            status_req.user_name = user_name
            status_req.kernel_slug = kernel_slug
            status_resp = get_client().kernels.kernels_api_client.get_kernel_session_status(status_req)
            session_id = getattr(status_resp, "kernel_session_id", None)
            if session_id:
                req.kernel_session_id = session_id
            resp = get_client().kernels.kernels_api_client.cancel_kernel_session(req)
            err = getattr(resp, "error_message", None)
            if err:
                return f"Cancel failed: {err}"
            return "Session cancelled."
        except Exception as e:
            return f"Error cancelling session: {e}"

    @mcp.tool()
    def competition_top_kernels(competition: str, sort_by: str = "scoreDescending", page_size: int = 20) -> str:
        """List top public kernels/notebooks for a competition, sorted by public score.

        Note: Kaggle API does not return the score value for active competitions,
        but DOES sort by score. Scores shown are extracted from notebook titles
        (e.g. '[44/50]', '[0.371]') where authors include them.

        Args:
            competition: Competition URL suffix (e.g. 'titanic').
            sort_by: Sort order — scoreDescending (default), scoreAscending,
                     voteCount, hotness, dateCreated, dateRun, commentCount.
            page_size: Number of results (max 100).
        """
        import re
        from kagglesdk.kernels.services.kernels_api_service import ApiListKernelsRequest
        from kagglesdk.kernels.types.kernels_api_service import KernelsListSortType

        _sort_map = {
            "voteCount": KernelsListSortType.VOTE_COUNT,
            "hotness": KernelsListSortType.HOTNESS,
            "scoreDescending": KernelsListSortType.SCORE_DESCENDING,
            "scoreAscending": KernelsListSortType.SCORE_ASCENDING,
            "dateCreated": KernelsListSortType.DATE_CREATED,
            "dateRun": KernelsListSortType.DATE_RUN,
            "commentCount": KernelsListSortType.COMMENT_COUNT,
        }

        def _extract_score(title: str) -> str:
            # Match patterns like [44/50], [0.371], (score: 0.88), LB:0.95
            m = re.search(r'\[(\d+/\d+|\d+\.\d+)\]', title)
            if m:
                return m.group(1)
            m = re.search(r'(?:LB|score)[:\s]+(\d+\.\d+)', title, re.IGNORECASE)
            if m:
                return m.group(1)
            return ""

        try:
            req = ApiListKernelsRequest()
            req.competition = competition
            req.sort_by = _sort_map.get(sort_by, KernelsListSortType.SCORE_DESCENDING)
            req.page = 1

            resp = get_client().kernels.kernels_api_client.list_kernels(req)
            kernels = resp.kernels or []
            if not kernels:
                return f"No public kernels found for '{competition}'."

            lines = [f"**Top public kernels for `{competition}`** (sorted by {sort_by}):"]
            lines.append("*Score extracted from title where available; API does not return score values for active competitions.*\n")
            for i, k in enumerate(kernels[:page_size], 1):
                kd = k.to_dict() if hasattr(k, "to_dict") else {}
                ref = kd.get("ref", "")
                title = kd.get("title", ref)
                votes = kd.get("totalVotes", "N/A")
                api_score = kd.get("bestPublicScore")
                extracted = _extract_score(title)
                if api_score is not None:
                    score_str = f" | Score: {api_score}"
                elif extracted:
                    score_str = f" | Score: {extracted} (from title)"
                else:
                    score_str = ""
                lines.append(f"{i}. **{title}** (`{ref}`)\n   Votes: {votes}{score_str}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error listing kernels: {e}"
