<div align="center">

<img src="assets/logo.png" alt="kaggle-mcp logo" width="360">

<!-- mcp-name: io.github.Galaxy-Dawn/kaggle-mcp -->

全功能 Kaggle API MCP 服务器 — 涵盖竞赛、数据集、Notebook、模型、基准测试和讨论区的 51 个工具。

[![PyPI](https://img.shields.io/pypi/v/kaggle-mcp-server?color=blue)](https://pypi.org/project/kaggle-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/Galaxy-Dawn/kaggle-mcp)](https://github.com/Galaxy-Dawn/kaggle-mcp/stargazers)
[![GitHub last commit](https://img.shields.io/github/last-commit/Galaxy-Dawn/kaggle-mcp)](https://github.com/Galaxy-Dawn/kaggle-mcp/commits/master)

[English](README.md) | [中文](README.zh-CN.md)

</div>

## 为什么选择 kaggle-mcp？

Kaggle 提供了[官方远程 MCP 服务器](https://www.kaggle.com/docs/mcp)（`https://www.kaggle.com/mcp`）。以下是 kaggle-mcp 与官方的对比：

| 功能 | kaggle-mcp | [Kaggle 官方 MCP](https://www.kaggle.com/docs/mcp) |
|------|:----------:|:----------:|
| 工具总数 | **51** | **51+** |
| 讨论区（10 个工具） | ✅ | ❌ |
| Kernel Session 管理 | ✅ | ✅ |
| 模型 CRUD + 实例管理 | ✅ | ✅ |
| 数据集创建/版本管理 | ✅ | ✅ |
| 基准测试排行榜 | ✅ | ✅ |
| AI 驱动的基准任务创建 | ❌ | ✅ |
| 架构 | 本地（stdio） | 远程 HTTP |
| 安装 | `uvx kaggle-mcp-server` | 需要 `npx mcp-remote` |
| 无远程 MCP 依赖 | ✅ | ❌ |
| 认证方式 | API Token | OAuth 2.0 / Token |

**适合使用 kaggle-mcp 的场景：** 需要讨论区工具（官方 MCP 完全不支持），或希望使用无远程依赖的本地 stdio 架构。

**适合使用官方 MCP 的场景：** 偏好 OAuth 2.0 认证、希望零本地安装，或需要 AI 驱动的基准任务创建功能。

<p align="center">
  <img src="assets/architecture.svg" alt="kaggle-mcp architecture" width="700">
</p>

## 快速导航

| 章节 | 说明 |
|------|------|
| [前置条件](#前置条件) | Kaggle API Token 配置 |
| [安装](#安装) | uvx / pip / 源码 |
| [配置](#配置) | Claude Desktop、Claude Code、VS Code、Cursor |
| [工具 (51)](#工具-51) | 竞赛、数据集、Notebook、模型、基准测试、讨论区 |
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

## 工具 (51)

### 竞赛 (10)

| 工具 | 说明 |
|------|------|
| `competitions_list` | 搜索和列出 Kaggle 竞赛 |
| `competition_files` | 列出竞赛的数据文件 |
| `competition_download` | 下载竞赛数据文件 |
| `competition_submit` | 提交预测结果 |
| `competition_submissions` | 查看提交历史 |
| `competition_leaderboard` | 查看排行榜（前 20 名） |
| `competition_get` | 获取竞赛详细信息 |
| `competition_data_summary` | 获取数据文件摘要 |
| `competition_get_submission` | 获取单个提交详情 |
| `competition_leaderboard_download` | 下载完整排行榜 CSV |

<details>
<summary>参数详情</summary>

1. **competitions_list** — `search`、`category`、`sort_by`（`latestDeadline`/`numberOfTeams`/`recentlyCreated`）、`page`
2. **competition_files** — `competition`（URL 后缀，如 `titanic`）
3. **competition_download** — `competition`、`file_name`（可选，留空下载全部）→ 下载链接
4. **competition_submit** — `competition`、`blob_file_tokens`、`message`
5. **competition_submissions** — `competition`
6. **competition_leaderboard** — `competition` → 前 20 名队伍和分数
7. **competition_get** — `competition` → 完整详情（截止日期、奖励、评估指标等）
8. **competition_data_summary** — `competition` → 数据文件摘要字典
9. **competition_get_submission** — `competition`、`submission_id`（整数）
10. **competition_leaderboard_download** — `competition` → 完整排行榜 CSV 下载链接

</details>

### 数据集 (11)

| 工具 | 说明 |
|------|------|
| `datasets_list` | 搜索和列出 Kaggle 数据集 |
| `dataset_files` | 列出数据集中的文件 |
| `dataset_download` | 下载数据集文件 |
| `dataset_metadata` | 获取数据集元数据 |
| `dataset_create` | 创建新数据集 |
| `file_upload` | 上传文件到 Kaggle |
| `dataset_get` | 获取数据集完整信息 |
| `dataset_create_version` | 创建新数据集版本 |
| `dataset_update_metadata` | 更新数据集标题/描述 |
| `dataset_delete` | 删除数据集 |
| `dataset_download_file` | 下载数据集中的单个文件 |

<details>
<summary>参数详情</summary>

1. **datasets_list** — `search`、`sort_by`（`hottest`/`votes`/`updated`/`active`）、`file_type`、`page`
2. **dataset_files** — `owner`、`dataset_slug`
3. **dataset_download** — `owner`、`dataset_slug`、`file_name`（可选）→ 下载链接
4. **dataset_metadata** — `owner`、`dataset_slug` → 元数据字典
5. **dataset_create** — `owner`、`slug`、`title`、`file_tokens`（来自 `file_upload`）、`license_name`、`is_private`
6. **file_upload** — `file_name`、`content` → 用于 `dataset_create` 的文件 Token
7. **dataset_get** — `owner`、`dataset_slug` → 完整数据集详情
8. **dataset_create_version** — `owner`、`dataset_slug`、`version_notes`、`file_tokens`
9. **dataset_update_metadata** — `owner`、`dataset_slug`、`title`、`description`
10. **dataset_delete** — `owner`、`dataset_slug`
11. **dataset_download_file** — `owner`、`dataset_slug`、`file_name` → 下载链接

</details>

### Notebook (9)

| 工具 | 说明 |
|------|------|
| `kernels_list` | 搜索和列出 Notebook/Kernel |
| `kernel_pull` | 获取 Notebook 源代码 |
| `kernel_push` | 推送/保存 Notebook 到 Kaggle |
| `kernel_output` | 获取 Kernel 输出下载链接 |
| `kernel_session_create` | 创建交互式 Kernel Session |
| `kernel_session_status` | 查询 Session 执行状态 |
| `kernel_session_output` | 列出 Session 输出文件 |
| `kernel_session_cancel` | 取消正在运行的 Session |
| `competition_top_kernels` | 列出竞赛得分最高的公开 Notebook |

<details>
<summary>参数详情</summary>

1. **kernels_list** — `search`、`competition`、`dataset`、`sort_by`（`hotness`/`commentCount`/`dateCreated`/`dateRun`/`relevance`/`voteCount`）、`page`
2. **kernel_pull** — `user_name`、`kernel_slug` → 元数据 + 源代码
3. **kernel_push** — `title`、`text`、`language`（`python`/`r`）、`kernel_type`（`notebook`/`script`）、`is_private`
4. **kernel_output** — `user_name`、`kernel_slug` → 下载链接
5. **kernel_session_create** — `user_name`、`kernel_slug` → Session 详情
6. **kernel_session_status** — `user_name`、`kernel_slug` → 状态 + 失败信息
7. **kernel_session_output** — `user_name`、`kernel_slug` → 输出文件列表及链接
8. **kernel_session_cancel** — `user_name`、`kernel_slug`
9. **competition_top_kernels** — `competition`、`sort_by`（`scoreDescending`/`scoreAscending`/`voteCount`/`hotness`/`dateCreated`/`dateRun`/`commentCount`）、`page_size`

</details>

### 模型 (10)

| 工具 | 说明 |
|------|------|
| `models_list` | 搜索和列出 Kaggle 模型 |
| `model_get` | 获取模型详细信息 |
| `model_create` | 创建新模型 |
| `model_update` | 更新模型元数据 |
| `model_delete` | 删除模型 |
| `model_instances_list` | 列出模型的所有实例 |
| `model_instance_get` | 获取特定模型实例 |
| `model_instance_create` | 创建新模型实例 |
| `model_instance_versions` | 列出模型实例的版本 |
| `model_instance_version_create` | 创建新模型实例版本 |

<details>
<summary>参数详情</summary>

1. **models_list** — `search`、`owner`、`sort_by`（`hotness`/`downloadCount`/`createTime`/`updateTime`）、`page_size`
2. **model_get** — `owner`、`model_slug`
3. **model_create** — `owner`、`slug`、`title`、`subtitle`、`is_private`、`description`
4. **model_update** — `owner`、`model_slug`、`title`、`subtitle`、`description`
5. **model_delete** — `owner`、`model_slug`
6. **model_instances_list** — `owner`、`model_slug`
7. **model_instance_get** — `owner`、`model_slug`、`framework`、`instance_slug`
8. **model_instance_create** — `owner`、`model_slug`、`framework`、`instance_slug`、`license_name`、`is_private`
9. **model_instance_versions** — `owner`、`model_slug`、`framework`、`instance_slug`
10. **model_instance_version_create** — `owner`、`model_slug`、`framework`、`instance_slug`、`version_notes`、`file_tokens`

</details>

### 基准测试 (1)

| 工具 | 说明 |
|------|------|
| `benchmark_leaderboard` | 获取基准测试排行榜 |

<details>
<summary>参数详情</summary>

1. **benchmark_leaderboard** — `owner_slug`、`benchmark_slug`、`version_number`（可选，默认 `0`）

</details>

### 讨论区 (10)

| 工具 | 说明 |
|------|------|
| `discussions_search` | 搜索 Kaggle 讨论 |
| `discussions_list` | 列出竞赛/数据集的讨论 |
| `discussion_detail` | 按 ID 获取讨论内容 |
| `discussion_comments` | 获取讨论评论 |
| `discussion_comments_search` | 跨讨论搜索评论内容 |
| `discussions_by_source` | 按来源类型浏览讨论 |
| `discussions_solutions` | 浏览竞赛解决方案 write-ups |
| `discussions_writeups` | 按类型浏览 Kaggle write-ups |
| `discussions_trending` | 浏览热门讨论 |
| `discussions_my` | 列出当前用户的讨论 |

<details>
<summary>参数详情</summary>

1. **discussions_search** — `query`、`sort_by`（`hotness`/`votes`/`comments`/`created`/`updated`）、`source_type`、`page_size`
2. **discussions_list** — `competition`、`dataset`、`page_size`、`since_hours`（过滤最近 N 小时）、`new_only`（按 `createTime` 过滤）
3. **discussion_detail** — `discussion_id`（整数）、`competition`（推荐填写以提高准确性）
4. **discussion_comments** — `discussion_id`、`page_size`
5. **discussion_comments_search** — `query`、`page_size`
6. **discussions_by_source** — `source_type`（`competition`/`dataset`/`kernel`/`site_forum`/`competition_solution`/`model`/`write_up`/`learn_track`/`benchmark`/`benchmark_task`）、`query`、`sort_by`、`page_size`
7. **discussions_solutions** — `competition`（可选 slug）、`sort_by`、`page_size`
8. **discussions_writeups** — `write_up_type`（`knowledge`/`competition_solution`/`hackathon`/`personal_project`/`forum_topic`/`blog`）、`query`、`page_size`
9. **discussions_trending** — `source_type`（可选）、`page_size`
10. **discussions_my** — `page_size`

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
