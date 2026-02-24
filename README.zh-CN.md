<div align="center">

<img src="assets/logo.png" alt="kaggle-mcp logo" width="360">

<!-- mcp-name: io.github.Galaxy-Dawn/kaggle-mcp -->

全功能 Kaggle API MCP 服务器 — 涵盖竞赛、数据集、Notebook、模型和讨论区的 21 个工具。

[![PyPI](https://img.shields.io/pypi/v/kaggle-mcp-server?color=blue)](https://pypi.org/project/kaggle-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Galaxy-Dawn/kaggle-mcp)](https://github.com/Galaxy-Dawn/kaggle-mcp/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/Galaxy-Dawn/kaggle-mcp)](https://github.com/Galaxy-Dawn/kaggle-mcp/commits/master)

[English](README.md) | [中文](README.zh-CN.md)

</div>

<p align="center">
  <img src="assets/architecture.svg" alt="kaggle-mcp architecture" width="700">
</p>

## 为什么选择 kaggle-mcp？

Kaggle 提供了[官方远程 MCP 服务器](https://www.kaggle.com/docs/mcp)（`https://www.kaggle.com/mcp`）。以下是 kaggle-mcp 与官方的对比：

| 功能 | kaggle-mcp | [Kaggle 官方 MCP](https://www.kaggle.com/docs/mcp) |
|------|:----------:|:----------:|
| 工具总数 | **21** | ~15 |
| 讨论区（搜索/列表/详情/评论） | ✅ 4 个工具 | ❌ |
| 数据集创建与文件上传 | ✅ | ❌ |
| 架构 | 本地（stdio） | 远程 HTTP |
| 安装 | `uvx kaggle-mcp-server` | 需要 `npx mcp-remote` |
| 无远程 MCP 依赖 | ✅ | ❌ |
| 认证方式 | API Token | OAuth 2.0 / Token |

**适合使用 kaggle-mcp 的场景：** 需要讨论区工具、数据集创建/上传，或需要无远程 MCP 依赖的原生 stdio 支持。

**适合使用官方 MCP 的场景：** 偏好 OAuth 2.0 认证，或希望零本地安装。

## 快速导航

| 章节 | 说明 |
|------|------|
| [前置条件](#前置条件) | Kaggle API Token 配置 |
| [安装](#安装) | uvx / pip / 源码 |
| [配置](#配置) | Claude Desktop、Claude Code、VS Code、Cursor |
| [工具 (21)](#工具-21) | 竞赛、数据集、Notebook、模型、讨论区 |
| [调试](#调试) | MCP Inspector |
| [开发](#开发) | 本地开发环境搭建 |

## 前置条件

需要 Kaggle API Token，支持以下两种认证方式：

<details>
<summary><b>方式 A：API Token（推荐）</b></summary>

1. 前往 https://www.kaggle.com/settings → API → Create New API Token
2. 设置环境变量：

```bash
export KAGGLE_API_TOKEN="KGAT_xxxxxxxxxxxx"
```

</details>

<details>
<summary><b>方式 B：kaggle.json</b></summary>

从 Kaggle 设置页面下载 Token 文件，会保存到 `~/.kaggle/kaggle.json`：

```json
{"username": "your_username", "key": "your_api_key"}
```

</details>

## 安装

> **注意：** MCP 服务器由 MCP 客户端（Claude Code、VS Code 等）自动启动 — **无需在终端手动运行**。以下命令是客户端在后台使用的。

### 使用 uvx（推荐）

无需安装。[uvx](https://docs.astral.sh/uv/guides/tools/) 会自动下载并运行服务器：

```bash
# MCP 客户端内部使用；无需手动运行
uvx kaggle-mcp-server
```

### 使用 pip

```bash
pip install kaggle-mcp-server
```

### 从源码安装

```bash
git clone https://github.com/Galaxy-Dawn/kaggle-mcp.git
cd kaggle-mcp
uv sync
```

## 配置

### Claude Desktop

添加到 `claude_desktop_config.json`：

<details>
<summary>使用 uvx（推荐）</summary>

```json
{
  "mcpServers": {
    "kaggle": {
      "command": "uvx",
      "args": ["kaggle-mcp-server"],
      "env": {
        "KAGGLE_API_TOKEN": "KGAT_xxxxxxxxxxxx"
      }
    }
  }
}
```

</details>

<details>
<summary>使用 pip</summary>

```json
{
  "mcpServers": {
    "kaggle": {
      "command": "python",
      "args": ["-m", "kaggle_mcp.server"],
      "env": {
        "KAGGLE_API_TOKEN": "KGAT_xxxxxxxxxxxx"
      }
    }
  }
}
```

</details>

### Claude Code

```bash
claude mcp add kaggle -- uvx kaggle-mcp-server
```

或添加到**项目的** `.mcp.json`（不是 `settings.json`）：

```json
{
  "mcpServers": {
    "kaggle": {
      "command": "uvx",
      "args": ["kaggle-mcp-server"],
      "env": {
        "KAGGLE_API_TOKEN": "KGAT_xxxxxxxxxxxx"
      }
    }
  }
}
```

### VS Code

[![Install with UV in VS Code](https://img.shields.io/badge/VS_Code-UV-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=kaggle&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22kaggle-mcp-server%22%5D%7D) [![Install with UV in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UV-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=kaggle&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22kaggle-mcp-server%22%5D%7D)

添加到 `.vscode/mcp.json`（注意：键名是 **`"servers"`**，不是 `"mcpServers"`）：

```json
{
  "servers": {
    "kaggle": {
      "command": "uvx",
      "args": ["kaggle-mcp-server"],
      "env": {
        "KAGGLE_API_TOKEN": "KGAT_xxxxxxxxxxxx"
      }
    }
  }
}
```

### Cursor

添加到 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "kaggle": {
      "command": "uvx",
      "args": ["kaggle-mcp-server"],
      "env": {
        "KAGGLE_API_TOKEN": "KGAT_xxxxxxxxxxxx"
      }
    }
  }
}
```

> **提示：** 如果你已经在 **shell 环境**（如 `.bashrc` 或 `.zshrc`）中设置了 `KAGGLE_API_TOKEN`，可以省略 `"env"` 配置块。

## 工具 (21)

### 竞赛 (6)

| 工具 | 说明 |
|------|------|
| `competitions_list` | 搜索和列出 Kaggle 竞赛 |
| `competition_files` | 列出竞赛的数据文件 |
| `competition_download` | 下载竞赛数据文件 |
| `competition_submit` | 提交预测结果 |
| `competition_submissions` | 查看提交历史 |
| `competition_leaderboard` | 查看排行榜（前 20 名） |

<details>
<summary>参数详情</summary>

1. **competitions_list** — 搜索和列出 Kaggle 竞赛。
   - 输入：
     - `search`（string，可选）：搜索关键词。
     - `category`（string，可选）：按类别筛选（如 `featured`、`research`、`playground`）。
     - `sort_by`（string，可选）：排序方式（`latestDeadline`、`numberOfTeams`、`recentlyCreated`）。
     - `page`（integer，可选）：分页页码，默认 `1`。
   - 返回：竞赛列表，包含标题、引用、类别、截止日期和队伍数。

2. **competition_files** — 列出竞赛的数据文件。
   - 输入：
     - `competition`（string，必填）：竞赛 URL 后缀（如 `titanic`）。
   - 返回：文件名和大小列表。

3. **competition_download** — 下载竞赛数据文件，返回下载链接。
   - 输入：
     - `competition`（string，必填）：竞赛 URL 后缀。
     - `file_name`（string，可选）：指定文件名，留空下载全部。
   - 返回：下载链接。

4. **competition_submit** — 提交预测结果。
   - 输入：
     - `competition`（string，必填）：竞赛 URL 后缀。
     - `blob_file_tokens`（string，必填）：上传后获得的文件 Token。
     - `message`（string，必填）：提交描述信息。
   - 返回：提交结果详情。

5. **competition_submissions** — 查看竞赛提交历史。
   - 输入：
     - `competition`（string，必填）：竞赛 URL 后缀。
   - 返回：提交列表，包含日期、分数、状态和描述。

6. **competition_leaderboard** — 查看竞赛排行榜（前 20 名）。
   - 输入：
     - `competition`（string，必填）：竞赛 URL 后缀。
   - 返回：前 20 名队伍名称和分数。

</details>

### 数据集 (6)

| 工具 | 说明 |
|------|------|
| `datasets_list` | 搜索和列出 Kaggle 数据集 |
| `dataset_files` | 列出数据集中的文件 |
| `dataset_download` | 下载数据集文件 |
| `dataset_metadata` | 获取数据集元数据 |
| `dataset_create` | 创建新数据集 |
| `file_upload` | 上传文件到 Kaggle |

<details>
<summary>参数详情</summary>

1. **datasets_list** — 搜索和列出 Kaggle 数据集。
   - 输入：
     - `search`（string，可选）：搜索关键词。
     - `sort_by`（string，可选）：排序方式（`hottest`、`votes`、`updated`、`active`）。
     - `file_type`（string，可选）：按文件类型筛选（`csv`、`json`、`sqlite` 等）。
     - `page`（integer，可选）：分页页码，默认 `1`。
   - 返回：数据集列表，包含标题、引用、大小和下载次数。

2. **dataset_files** — 列出数据集中的文件。
   - 输入：
     - `owner`（string，必填）：数据集所有者用户名。
     - `dataset_slug`（string，必填）：数据集 slug 名称。
   - 返回：文件名和大小列表。

3. **dataset_download** — 下载数据集文件，返回下载链接。
   - 输入：
     - `owner`（string，必填）：数据集所有者用户名。
     - `dataset_slug`（string，必填）：数据集 slug 名称。
     - `file_name`（string，可选）：指定文件名，留空下载全部。
   - 返回：下载链接。

4. **dataset_metadata** — 获取数据集元数据。
   - 输入：
     - `owner`（string，必填）：数据集所有者用户名。
     - `dataset_slug`（string，必填）：数据集 slug 名称。
   - 返回：数据集元数据字典。

5. **dataset_create** — 创建新数据集。需先使用 `file_upload` 获取文件 Token。
   - 输入：
     - `owner`（string，必填）：所有者用户名。
     - `slug`（string，必填）：数据集 slug。
     - `title`（string，必填）：数据集标题。
     - `file_tokens`（string，可选）：`file_upload` 返回的文件 Token，多个用逗号分隔。
     - `license_name`（string，可选）：许可证（如 `CC0-1.0`、`CC-BY-SA-4.0`），默认 `CC0-1.0`。
     - `is_private`（boolean，可选）：是否私有，默认 `true`。
   - 返回：创建结果详情。

6. **file_upload** — 上传文件到 Kaggle，获取用于 `dataset_create` 的 Token。
   - 输入：
     - `file_name`（string，必填）：文件名（如 `data.csv`、`config.json`）。
     - `content`（string，必填）：文件内容（文本）。
   - 返回：文件 Token 字符串。

</details>

### Notebook (3)

| 工具 | 说明 |
|------|------|
| `kernels_list` | 搜索和列出 Notebook/Kernel |
| `kernel_pull` | 获取 Notebook 源代码 |
| `kernel_push` | 推送/保存 Notebook 到 Kaggle |

<details>
<summary>参数详情</summary>

1. **kernels_list** — 搜索和列出 Kaggle Notebook/Kernel。
   - 输入：
     - `search`（string，可选）：搜索关键词。
     - `competition`（string，可选）：按竞赛筛选。
     - `dataset`（string，可选）：按数据集筛选。
     - `sort_by`（string，可选）：排序方式（`hotness`、`commentCount`、`dateCreated`、`dateRun`、`relevance`、`voteCount`）。
     - `page`（integer，可选）：分页页码，默认 `1`。
   - 返回：Kernel 列表，包含标题、引用、投票数和语言。

2. **kernel_pull** — 获取 Notebook 源代码。
   - 输入：
     - `user_name`（string，必填）：Kernel 所有者用户名。
     - `kernel_slug`（string，必填）：Kernel slug 名称。
   - 返回：Kernel 元数据和源代码。

3. **kernel_push** — 推送/保存 Notebook 到 Kaggle。
   - 输入：
     - `title`（string，必填）：Notebook 标题。
     - `text`（string，必填）：Notebook 源代码。
     - `language`（string，可选）：语言（`python`、`r`），默认 `python`。
     - `kernel_type`（string，可选）：类型（`notebook`、`script`），默认 `notebook`。
     - `is_private`（boolean，可选）：是否私有，默认 `true`。
   - 返回：推送结果详情。

</details>

### 模型 (2)

| 工具 | 说明 |
|------|------|
| `models_list` | 搜索和列出 Kaggle 模型 |
| `model_get` | 获取模型详细信息 |

<details>
<summary>参数详情</summary>

1. **models_list** — 搜索和列出 Kaggle 模型。
   - 输入：
     - `search`（string，可选）：搜索关键词。
     - `owner`（string，可选）：按所有者筛选。
     - `sort_by`（string，可选）：排序方式（`hotness`、`downloadCount`、`createTime`、`updateTime`）。
     - `page_size`（integer，可选）：每页结果数，默认 `20`。
   - 返回：模型列表，包含标题和引用。

2. **model_get** — 获取特定模型的详细信息。
   - 输入：
     - `owner`（string，必填）：模型所有者用户名。
     - `model_slug`（string，必填）：模型 slug 名称。
   - 返回：模型元数据字典。

</details>

### 讨论区 (4)

| 工具 | 说明 |
|------|------|
| `discussions_search` | 搜索 Kaggle 讨论 |
| `discussions_list` | 列出竞赛/数据集的讨论 |
| `discussion_detail` | 按 ID 获取讨论内容 |
| `discussion_comments` | 获取讨论评论 |

<details>
<summary>参数详情</summary>

1. **discussions_search** — 搜索 Kaggle 讨论。
   - 输入：
     - `query`（string，必填）：搜索关键词。
     - `page_size`（integer，可选）：结果数量（最大 50），默认 `20`。
   - 返回：讨论列表，包含 ID、标题和投票数。

2. **discussions_list** — 列出竞赛或数据集的讨论。
   - 输入：
     - `competition`（string，可选）：竞赛 slug。
     - `dataset`（string，可选）：数据集引用。
     - `page_size`（integer，可选）：结果数量（最大 50），默认 `20`。
   - 返回：讨论列表，包含 ID、标题和投票数。

3. **discussion_detail** — 按 ID 获取讨论内容。
   - 输入：
     - `discussion_id`（integer，必填）：讨论的数字 ID。
   - 返回：讨论标题、作者、投票数、论坛和正文内容。

4. **discussion_comments** — 获取讨论评论。
   - 输入：
     - `discussion_id`（integer，必填）：讨论的数字 ID。
   - 返回：讨论评论页面链接。

</details>

## 调试

使用 [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) 调试服务器：

```bash
npx @modelcontextprotocol/inspector uvx kaggle-mcp-server
```

Inspector 会提供一个浏览器 URL 用于访问调试工具。

## 开发

```bash
git clone https://github.com/Galaxy-Dawn/kaggle-mcp.git
cd kaggle-mcp
uv sync
```

然后在 MCP 客户端中使用本地路径配置服务器，或使用 [MCP Inspector](#调试) 进行测试。

## 贡献

欢迎贡献！请在 [GitHub 仓库](https://github.com/Galaxy-Dawn/kaggle-mcp) 上提交 Issue 或 Pull Request。

## 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。
