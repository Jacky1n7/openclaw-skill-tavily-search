<div align="center">

# ⚡ Tavily 搜索 Skill（OpenClaw）

**由 Tavily 驱动，面向 OpenClaw 多智能体/工具链使用。**

[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-8A2BE2?style=for-the-badge)](https://docs.openclaw.ai)
[![Tavily](https://img.shields.io/badge/Tavily-API-00E5FF?style=for-the-badge)](https://tavily.com)
[![Python](https://img.shields.io/badge/Python-3.x-FF2BD6?style=for-the-badge)](https://www.python.org/)

</div>

---

## ✨ 这是什么？

这是一个 **OpenClaw Skill**，通过 **Tavily Search API** 实现网页搜索。

适合在你不想使用 Brave Search 的场景下，作为可替代的“联网搜索”能力：输出结构化结果（title/url/snippet），便于下游 Agent 做引用、总结、写作与审稿。

---

## 🔑 配置（必需）

你需要提供 Tavily API Key（二选一）：

1) 环境变量：
- `TAVILY_API_KEY=...`

2) 本地配置文件（推荐 OpenClaw 主机使用）：
- `~/.openclaw/.env`

示例：

```bash
mkdir -p ~/.openclaw
printf 'TAVILY_API_KEY=你的TOKEN\n' >> ~/.openclaw/.env
chmod 600 ~/.openclaw/.env
```

---

## 🚀 用法

### 1) 默认输出（raw JSON）

```bash
python3 skill/scripts/tavily_search.py --query "OpenClaw 中文社区" --max-results 5
```

### 2) 稳定结构输出（推荐，brave-like）

输出结构：

```json
{ "query": "...", "results": [ {"title": "...", "url": "...", "snippet": "..."} ] }
```

命令：

```bash
python3 skill/scripts/tavily_search.py --query "multi-agent workflow" --max-results 5 --format brave
```

### 3) 可读 Markdown 列表

```bash
python3 skill/scripts/tavily_search.py --query "OpenClaw" --max-results 5 --format md
```

---

## 📦 打包产物（可分发）

仓库 `dist/` 下包含：

- `dist/tavily-search.skill`：打包好的 skill（zip bundle）
- `dist/tavily-search.manifest.json`：sha256 清单（用于校验完整性）

本地重新打包：

```bash
rm -f dist/tavily-search.skill
(cd skill && zip -qr ../dist/tavily-search.skill .)
```

---

## 🧪 输出示例

<details>
<summary>点击展开</summary>

```text
1. 标题...
   https://example.com
   - 摘要片段...
```

</details>

---

## 🦐 备注（建议实践）

- `--max-results` 建议默认 3–5，够用且省 token。
- 需要更深覆盖时使用：`--search-depth advanced`。

---

## License

MIT
