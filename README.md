<div align="center">

<img src="assets/banner.svg" alt="Tavily Search Skill Banner" width="100%" />

# ⚡ Tavily 搜索 Skill（OpenClaw）

**由 Tavily 驱动，面向 OpenClaw 多智能体/工具链使用。**

[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-8A2BE2?style=for-the-badge)](https://docs.openclaw.ai)
[![Tavily](https://img.shields.io/badge/Tavily-API-00E5FF?style=for-the-badge)](https://tavily.com)
[![Python](https://img.shields.io/badge/Python-3.x-FF2BD6?style=for-the-badge)](https://www.python.org/)

</div>

---

## 📌 目录导航

- [✨ 这是什么？](#-这是什么)
- [🔑 配置（必需）](#-配置必需)
- [⚡ 一键安装（推荐）](#-一键安装推荐)
- [🚀 用法](#-用法)
- [📦 打包产物（可分发）](#-打包产物可分发)
- [🧪 输出示例](#-输出示例)
- [🦐 备注（建议实践）](#-备注建议实践)
- [License](#license)

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

## ⚡ 一键安装（推荐）

> 目标：用户尽量少操作，直接装进 OpenClaw 的 skills 目录即可使用。

### 方式 0（最便携）：ClawHub 一行安装（推荐分发方式）

当这个 skill 发布到 ClawHub 后，用户可以直接运行：

```bash
# 首次使用需要登录
clawhub login

# 默认：安装到“当前目录”的 skills/openclaw-tavily-search
clawhub install openclaw-tavily-search

# 推荐：显式安装到 OpenClaw workspace（更不容易装错位置）
clawhub --workdir ~/.openclaw/workspace --dir skills install openclaw-tavily-search
```

> 提示：如果你已经在 `~/.openclaw/workspace` 目录下，也可以直接运行默认安装命令。

### 方式 A：下载打包产物（`.skill`）并解压到 workspace

```bash
# 1) 下载
curl -L \
  -o /tmp/tavily-search.skill \
  https://raw.githubusercontent.com/Jacky1n7/openclaw-skill-tavily-search/main/dist/tavily-search.skill

# 2) 安装到 OpenClaw workspace（目录不存在会自动创建）
mkdir -p ~/.openclaw/workspace/skills/tavily-search
unzip -o /tmp/tavily-search.skill -d ~/.openclaw/workspace/skills/tavily-search

# 3) 验证
python3 ~/.openclaw/workspace/skills/tavily-search/scripts/tavily_search.py --query "OpenClaw" --max-results 3 --format md
```

### 方式 B：git clone（适合想改代码/发 PR）

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills

git clone https://github.com/Jacky1n7/openclaw-skill-tavily-search.git tavily-search-repo

# 只把 skill 目录放到 skills/tavily-search
rm -rf tavily-search
cp -R tavily-search-repo/skill tavily-search

python3 tavily-search/scripts/tavily_search.py --query "OpenClaw" --max-results 3 --format md
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

> 备注：`.skill` 本质上是一个 zip bundle，适合发到群里/邮件里/Release 里。

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
