"""Benchmark tools for Kaggle MCP Server."""

from mcp.server.fastmcp import FastMCP

from .client import get_client


def register(mcp: FastMCP) -> None:
    """Register benchmark tools."""

    @mcp.tool()
    def benchmark_leaderboard(
        owner_slug: str,
        benchmark_slug: str,
        version_number: int = 0,
    ) -> str:
        """Get the leaderboard for a Kaggle benchmark.

        Args:
            owner_slug: Benchmark owner username or organization slug.
            benchmark_slug: Benchmark slug name.
            version_number: Specific version number (0 for latest).
        """
        try:
            from kagglesdk.benchmarks.services.benchmarks_api_service import (
                BenchmarksApiClient,
            )
            from kagglesdk.benchmarks.types.benchmarks_api_service import (
                ApiGetBenchmarkLeaderboardRequest,
            )

            req = ApiGetBenchmarkLeaderboardRequest()
            req.owner_slug = owner_slug
            req.benchmark_slug = benchmark_slug
            if version_number > 0:
                req.version_number = version_number

            resp = get_client().benchmarks.benchmarks_api_client.get_benchmark_leaderboard(req)
            rows = resp.rows
            if not rows:
                return "No leaderboard data found."

            lines = [f"## Benchmark Leaderboard: {owner_slug}/{benchmark_slug}"]
            if version_number > 0:
                lines[0] += f" (v{version_number})"
            lines.append("")

            for row in rows:
                lines.append(f"**{row.model_version_name}** (`{row.model_version_slug}`)")
                if row.task_results:
                    for task in row.task_results:
                        result_str = str(task.result) if task.result else "N/A"
                        lines.append(
                            f"  - {task.benchmark_task_name} (v{task.task_version}): {result_str}"
                        )
                lines.append("")

            return "\n".join(lines).rstrip()
        except Exception as e:
            return f"Error fetching benchmark leaderboard: {e}"
