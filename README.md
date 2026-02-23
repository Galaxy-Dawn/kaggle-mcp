# kaggle-mcp

A full-featured MCP server wrapping the Kaggle API (20 tools across 5 modules).

## Installation

```bash
uv tool install kaggle-mcp
```

## Prerequisites

Configure Kaggle credentials at `~/.kaggle/kaggle.json`:

```json
{"username": "your_username", "key": "your_api_key"}
```

Get your API key from https://www.kaggle.com/settings → API → Create New Token.

## Claude Code Integration

Add to your Claude Code settings:

```json
"mcpServers": {
  "kaggle": {
    "command": "uv",
    "args": ["tool", "run", "kaggle-mcp"]
  }
}
```

## Tools (20)

### Competitions (6)

| Tool | Description |
|------|-------------|
| `competitions_list` | Search/list competitions |
| `competition_files` | List competition data files |
| `competition_download` | Download competition data |
| `competition_submit` | Submit predictions |
| `competition_submissions` | View submission history |
| `competition_leaderboard` | View leaderboard |

### Datasets (5)

| Tool | Description |
|------|-------------|
| `datasets_list` | Search/list datasets |
| `dataset_files` | List dataset files |
| `dataset_download` | Download dataset |
| `dataset_metadata` | Get metadata |
| `dataset_create` | Create dataset |

### Kernels (3)

| Tool | Description |
|------|-------------|
| `kernels_list` | Search/list notebooks |
| `kernel_pull` | Get notebook source |
| `kernel_push` | Push notebook |

### Models (2)

| Tool | Description |
|------|-------------|
| `models_list` | Search/list models |
| `model_get` | Get model details |

### Discussions (4)

| Tool | Description |
|------|-------------|
| `discussions_search` | Search discussions |
| `discussions_list` | List discussions by competition/dataset |
| `discussion_detail` | Get discussion content |
| `discussion_comments` | Get discussion comments |

## Development

```bash
git clone https://github.com/yourusername/kaggle-mcp.git
cd kaggle-mcp
uv sync
uv run kaggle-mcp
```

## License

MIT
