# personal-agent-asset

个人 AI Agent 资产仓库：统一维护 skills、commands、subagents、全局规则、MCP 配置等，
并通过一键脚本安装到 **Claude Code / Codex / Cursor / Trae** 等不同工具中。

## 设计原则

1. **单一源（Single Source of Truth）**：所有资产只在本仓库维护一份，不针对每个工具复制粘贴。
2. **以开放标准为主格式**：Skill 采用 [Agent Skills](https://agentskills.io) 的 `SKILL.md` 格式，
   主流工具都已支持或正在支持；全局规则以 `AGENTS.md` 为主格式。
3. **工具差异集中在 `adapters/`**：各工具的安装路径、格式转换都放在对应 adapter 里，资产本身保持工具无关。
4. **默认软链接安装**：安装时把资产 symlink 到各工具的配置目录，之后 `git pull` 即可同步更新。

## 目录结构

```
personal-agent-asset/
├── README.md
├── install.sh                  # 一键安装入口：./install.sh [claude|codex|cursor|trae|all]
│
├── skills/                     # ⭐ 核心资产：Agent Skills（SKILL.md 标准）
│   └── <skill-name>/
│       ├── SKILL.md            # 必需：frontmatter(name, description) + 指令
│       ├── scripts/            # 可选：skill 调用的脚本
│       ├── references/         # 可选：按需加载的参考文档
│       └── assets/             # 可选：模板、静态资源
│
├── commands/                   # 斜杠命令 / 可复用 prompt（Markdown）
│   └── <command-name>.md
│
├── agents/                     # Subagent 定义（Markdown + frontmatter）
│   └── <agent-name>.md
│
├── rules/                      # 全局指令 / 个人偏好
│   ├── AGENTS.md               # 主文件 → CLAUDE.md / AGENTS.md / Cursor rules
│   └── fragments/              # 可组合的规则片段（编码风格、语言偏好等）
│
├── mcp/                        # MCP server 配置（工具无关的统一描述）
│   └── servers.json            # 密钥用 ${ENV_VAR} 占位，不入库
│
├── hooks/                      # 生命周期 hook 脚本（目前主要用于 Claude Code）
│
├── adapters/                   # 各工具的安装逻辑，每个工具一个 install.sh
│   ├── claude-code/            # → ~/.claude/{skills,commands,agents,CLAUDE.md}
│   ├── codex/                  # → ~/.codex/{skills,prompts,AGENTS.md,config.toml}
│   ├── cursor/                 # → ~/.cursor/{skills,commands,agents,mcp.json}
│   └── trae/                   # → Trae 对应目录（待实现）
│
├── lib/
│   └── common.sh               # 安装公共函数：软链/复制、备份、卸载、dry-run
│
└── scripts/                    # 仓库维护工具
    ├── new-skill.sh            # 从模板创建新 skill
    ├── validate.sh             # 校验 SKILL.md frontmatter、脚本语法
    └── templates/              # 新建资产用的模板
```

### Adapter 约定

每个 `adapters/<tool>/install.sh` 会被 `install.sh` source，只需实现三个函数：

```bash
adapter_name()   { echo "Tool Name"; }          # 展示名
adapter_detect() { [ -d "$HOME/.tool" ]; }      # 本机是否安装了该工具
adapter_apply()  {                              # 同步资产
  sync_children "$REPO_ROOT/skills" "$HOME/.tool/skills"     # 目录下每个子项各建一个链接
  sync_item     "$REPO_ROOT/rules/AGENTS.md" "$HOME/.tool/AGENTS.md"  # 单个文件
}
```

`sync_*` 会自动处理安装/卸载、软链/复制、dry-run。如果目标位置已经有一个不归本仓库管理的文件，
会先备份成 `*.bak.<时间戳>` 再覆盖；卸载时只删除指向本仓库的软链接。

> 各工具的具体安装路径以 `adapters/<tool>/` 中的实现为准，工具升级后路径如有变化只需改 adapter。

## 资产映射

| 资产 | Claude Code | Codex | Cursor |
| --- | --- | --- | --- |
| `skills/` | `~/.claude/skills/` | `~/.codex/skills/` | `~/.cursor/skills/` |
| `commands/` | `~/.claude/commands/` | `~/.codex/prompts/` | `~/.cursor/commands/` |
| `agents/` | `~/.claude/agents/` | — | — |
| `rules/AGENTS.md` | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` | User Rules / `.cursor/rules/` |
| `mcp/servers.json` | `claude mcp add` / `~/.claude.json` | `~/.codex/config.toml` | `~/.cursor/mcp.json` |
| `hooks/` | `~/.claude/settings.json` | — | — |

## 使用方式

```bash
git clone git@github.com:plusgrey/personal-agent-asset.git ~/personal-agent-asset
cd ~/personal-agent-asset

./install.sh                # 安装到本机检测到的所有工具（等同 all）
./install.sh claude codex   # 只安装到指定工具
./install.sh --dry-run      # 只打印将要执行的操作，不做任何修改
./install.sh --copy         # 复制文件，不建软链接
./install.sh --uninstall    # 删除本仓库创建的软链接
./install.sh --force trae   # 未检测到该工具时也强制安装

git pull                    # 软链接模式下，拉取后即生效
```

## 新增一个 Skill

```bash
./scripts/new-skill.sh my-skill
# 编辑 skills/my-skill/SKILL.md
```

`SKILL.md` 最小示例：

```markdown
---
name: my-skill
description: 一句话说明这个 skill 做什么、什么时候该触发。
---

# My Skill

具体指令……
```

## Roadmap

- [x] 初始化仓库与目录规划
- [x] `install.sh` 框架 + 公共库（软链/复制/卸载/dry-run/备份）
- [x] Claude Code / Codex / Cursor adapter：skills、commands、agents、rules
- [x] `new-skill.sh`、`validate.sh`
- [ ] Trae adapter（确认 Trae 用户级目录）
- [ ] MCP：从 `mcp/servers.json` 生成各工具的配置
- [ ] Claude Code hooks 合并到 settings.json
- [ ] Cursor 全局 rules 方案
- [ ] CI 跑 `validate.sh`
