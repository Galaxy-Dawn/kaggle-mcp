"""Competition tools for Kaggle MCP Server."""

from mcp.server.fastmcp import FastMCP

from .client import get_client


def register(mcp: FastMCP) -> None:
    """Register competition tools."""

    @mcp.tool()
    def competitions_list(
        search: str = "",
        category: str = "",
        sort_by: str = "",
        page: int = 1,
    ) -> str:
        """Search and list Kaggle competitions.

        Args:
            search: Search term to filter competitions.
            category: Filter by category (e.g. featured, research, playground).
            sort_by: Sort order (latestDeadline, numberOfTeams, recentlyCreated).
            page: Page number for pagination.
        """
        from kagglesdk.competitions.services.competition_api_service import (
            ApiListCompetitionsRequest,
        )

        req = ApiListCompetitionsRequest()
        if search:
            req.search = search
        if category:
            req.category = category
        if sort_by:
            req.sort_by = sort_by
        req.page = page

        try:
            resp = get_client().competitions.competition_api_client.list_competitions(req)
        except Exception as e:
            return f"Error listing competitions: {e}"
        comps = resp.competitions
        if not comps:
            return "No competitions found."
        lines = []
        for c in comps:
            lines.append(
                f"- **{c.title}** (`{c.ref}`)\n"
                f"  Category: {c.category} | Deadline: {c.deadline} | Teams: {c.team_count}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def competition_files(competition: str) -> str:
        """List data files for a competition.

        Args:
            competition: Competition URL suffix (e.g. 'titanic').
        """
        from kagglesdk.competitions.services.competition_api_service import (
            ApiListDataFilesRequest,
        )

        req = ApiListDataFilesRequest()
        req.competition_name = competition
        try:
            resp = get_client().competitions.competition_api_client.list_data_files(req)
        except Exception as e:
            return f"Error listing competition files: {e}"
        files = resp.files
        if not files:
            return "No files found."
        lines = [f"- {f.name} ({getattr(f, 'total_bytes', 'N/A')} bytes)" for f in files]
        return "\n".join(lines)

    @mcp.tool()
    def competition_download(competition: str, file_name: str = "") -> str:
        """Download competition data files. Returns download URL.

        Args:
            competition: Competition URL suffix (e.g. 'titanic').
            file_name: Specific file to download. Empty for all files.
        """
        if file_name:
            from kagglesdk.competitions.services.competition_api_service import (
                ApiDownloadDataFileRequest,
            )

            req = ApiDownloadDataFileRequest()
            req.competition_name = competition
            req.file_name = file_name
            resp = get_client().competitions.competition_api_client.download_data_file(req)
        else:
            from kagglesdk.competitions.services.competition_api_service import (
                ApiDownloadDataFilesRequest,
            )

            req = ApiDownloadDataFilesRequest()
            req.competition_name = competition
            resp = get_client().competitions.competition_api_client.download_data_files(req)
        return f"Download URL: {resp.url}"

    @mcp.tool()
    def competition_submit(
        competition: str,
        blob_file_tokens: str,
        message: str,
    ) -> str:
        """Submit predictions to a competition.

        Args:
            competition: Competition URL suffix.
            blob_file_tokens: Blob file token from upload.
            message: Submission description message.
        """
        from kagglesdk.competitions.services.competition_api_service import (
            ApiCreateSubmissionRequest,
        )

        req = ApiCreateSubmissionRequest()
        req.competition_name = competition
        req.blob_file_tokens = blob_file_tokens
        req.submission_description = message
        resp = get_client().competitions.competition_api_client.create_submission(req)
        return str(resp.to_dict())

    @mcp.tool()
    def competition_submissions(competition: str) -> str:
        """View submission history for a competition.

        Args:
            competition: Competition URL suffix.
        """
        from kagglesdk.competitions.services.competition_api_service import (
            ApiListSubmissionsRequest,
        )

        req = ApiListSubmissionsRequest()
        req.competition_name = competition
        resp = get_client().competitions.competition_api_client.list_submissions(req)
        subs = resp.submissions
        if not subs:
            return "No submissions found."
        lines = []
        for s in subs:
            lines.append(
                f"- {s.date} | Score: {s.public_score} | Status: {s.status}\n"
                f"  {s.description}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def competition_leaderboard(competition: str) -> str:
        """View competition leaderboard (top 20).

        Args:
            competition: Competition URL suffix.
        """
        from kagglesdk.competitions.services.competition_api_service import (
            ApiGetLeaderboardRequest,
        )

        req = ApiGetLeaderboardRequest()
        req.competition_name = competition
        try:
            resp = get_client().competitions.competition_api_client.get_leaderboard(req)
        except Exception as e:
            return f"Error fetching leaderboard: {e}"
        subs = resp.submissions
        if not subs:
            return "No leaderboard data."
        lines = []
        for s in subs[:20]:
            lines.append(f"{s.team_name} - {s.score}")
        return "\n".join(lines)

    @mcp.tool()
    def competition_get(competition: str) -> str:
        """Get detailed competition info.

        Args:
            competition: Competition URL suffix (e.g. 'titanic').
        """
        from kagglesdk.competitions.services.competition_api_service import (
            ApiGetCompetitionRequest,
            ApiListCompetitionsRequest,
        )

        # Try the direct endpoint first
        try:
            req = ApiGetCompetitionRequest()
            req.competition_name = competition
            c = get_client().competitions.competition_api_client.get_competition(req)
            lines = [
                f"**{c.title}** (`{c.ref}`)",
                f"URL: {c.url}",
                f"Category: {c.category} | Reward: {c.reward}",
                f"Deadline: {c.deadline} | Teams: {c.team_count}",
                f"Evaluation: {c.evaluation_metric}",
                f"Max daily submissions: {c.max_daily_submissions}",
                f"Max team size: {c.max_team_size}",
                f"Kernels only: {c.is_kernels_submissions_only}",
                f"Description: {c.description}",
            ]
            return "\n".join(lines)
        except Exception:
            pass

        # Fallback: search by slug and return first match
        try:
            req2 = ApiListCompetitionsRequest()
            req2.search = competition
            resp = get_client().competitions.competition_api_client.list_competitions(req2)
            comps = resp.competitions or []
            # Exact slug match: ref ends with /<competition>
            match = next(
                (c for c in comps if (c.ref or "").rstrip("/").endswith("/" + competition)),
                None,
            )
            if not match:
                if not comps:
                    return f"Competition '{competition}' not found."
                candidates = "\n".join(
                    f"- {c.title} → `{(c.ref or '').rstrip('/').split('/')[-1]}`"
                    for c in comps[:5]
                )
                return f"Competition '{competition}' not found. Did you mean:\n{candidates}"
            c = match
            lines = [
                f"**{c.title}** (`{c.ref}`)",
                f"Category: {c.category} | Reward: {c.reward}",
                f"Deadline: {c.deadline} | Teams: {c.team_count}",
                f"Evaluation: {c.evaluation_metric}",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Error fetching competition info: {e}"

    @mcp.tool()
    def competition_data_summary(competition: str) -> str:
        """Get data files summary for a competition.

        Args:
            competition: Competition URL suffix (e.g. 'titanic').
        """
        try:
            from kagglesdk.competitions.services.competition_api_service import (
                ApiGetCompetitionDataFilesSummaryRequest,
            )

            req = ApiGetCompetitionDataFilesSummaryRequest()
            req.competition_name = competition
            resp = get_client().competitions.competition_api_client.get_competition_data_files_summary(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error fetching data summary: {e}"

    @mcp.tool()
    def competition_get_submission(competition: str, submission_id: int) -> str:
        """Get details for a single submission.

        Args:
            competition: Competition URL suffix (unused in routing, kept for context).
            submission_id: Numeric submission ID.
        """
        try:
            from kagglesdk.competitions.services.competition_api_service import (
                ApiGetSubmissionRequest,
            )

            req = ApiGetSubmissionRequest()
            req.ref = submission_id
            resp = get_client().competitions.competition_api_client.get_submission(req)
            return str(resp.to_dict())
        except Exception as e:
            return f"Error fetching submission: {e}"

    @mcp.tool()
    def competition_leaderboard_download(competition: str) -> str:
        """Download the full competition leaderboard. Returns download URL.

        Args:
            competition: Competition URL suffix (e.g. 'titanic').
        """
        try:
            from kagglesdk.competitions.services.competition_api_service import (
                ApiDownloadLeaderboardRequest,
            )

            req = ApiDownloadLeaderboardRequest()
            req.competition_name = competition
            resp = get_client().competitions.competition_api_client.download_leaderboard(req)
            return f"Download URL: {resp.url}"
        except Exception as e:
            return f"Error downloading leaderboard: {e}"
