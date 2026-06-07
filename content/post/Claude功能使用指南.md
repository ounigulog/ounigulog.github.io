---
# ── 必填 ──
title: 'Claude Code 终端功能使用指南'

# ── 时间 ──
date: 2026-06-07
lastmod: 2026-06-07

# ── 状态 ──
draft: false

# ── 分类 & 标签 ──
categories:
  - 工具指南
  - AI开发
tags:
  - Claude Code
  - 终端
  - 命令行
  - AI辅助开发

# ── SEO & 摘要 ──
description: 'Claude Code 终端中所有 "/" 斜杠命令的完整使用指南，按功能分类并附带实用示例。'
keywords:
  - Claude Code
  - 斜杠命令
  - 终端操作
  - AI编程助手

# ── 功能开关 ──
copyright: true
toc: true
math: false
mermaid: false
outdated: false
---

# Claude Code 终端功能使用指南

## 概述

在 Claude Code 终端中，输入 `/` 可呼出命令选择菜单。本文档将 **全部 70+ 个命令** 按功能分为 6 大类，逐一说明用途、参数和使用场景，并附实战工作流组合。

> **提示：** 在终端中随时输入 `/help` 可查看完整命令列表。部分命令背后对应着 **Skill（技能）**，由多个 AI 代理协同完成复杂任务。

---

## 1. 会话管理

管理对话的启动、暂停、导出、恢复与终止——日常使用频率最高的一类。

### 1.1 命令详表

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/help` | 显示所有可用命令和帮助信息 | 不记得命令名时首选 |
| `/clear` | 清空上下文并开启新会话 | 旧会话保留在磁盘，可通过 `/resume` 找回 |
| `/resume` | 从磁盘恢复之前保存的会话 | 支持从列表中选取目标会话 |
| `/rename` | 重命名当前会话 | 起有意义的名字便于日后检索 |
| `/compact` | 压缩历史对话以释放上下文窗口 | 摘要不会丢失关键信息，相当于"软清空" |
| `/rewind` | 将代码和/或对话回退到历史节点 | 类似 Git revert，回退错误操作 |
| `/branch` | 在当前位置创建对话分支 | 从同一点并行尝试不同方案 |
| `/fork` | 派生一个后台代理，继承全部上下文 | 子代理独立运行，不阻塞主会话 |
| `/background` | 将当前会话放入后台，释放终端 | 等同于终端 `Ctrl+Z` + `bg` |
| `/exit` | 退出 Claude Code CLI | — |
| `/btw` | 在不中断主对话的前提下快速提问 | "by the way"——适合临时查一个小知识点 |
| `/recap` | 生成当前会话的一行摘要 | 快速回顾本会话做了什么 |
| `/copy` | 复制最近一条回复到剪贴板 | `/copy N` 可指定倒数第 N 条 |
| `/export` | 导出对话为文件或复制到剪贴板 | 支持 Markdown / 纯文本格式 |
| `/focus` | 切换精简视图 | 仅显示提示词、摘要和回复，减少视觉干扰 |

### 1.2 常用示例

```bash
# 恢复上一次对话继续工作
/resume

# 复制倒数第 3 条回复
/copy 3

# 开始全新会话（旧会话仍在磁盘保留）
/clear

# 临时查一个 API 用法，不污染主对话
/btw Python subprocess.run 如何设置超时
```

---

## 2. 界面与显示

定制终端外观，查看系统状态、资源消耗和后台任务。

### 2.1 命令详表

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/theme` | 切换终端主题配色 | 适配亮/暗环境 |
| `/color` | 设置当前会话提示栏颜色 | 多会话并开时便于区分 |
| `/tui` | 切换终端 UI 渲染模式 | `default`（标准）/ `fullscreen`（全屏） |
| `/context` | 以彩色网格可视化当前上下文使用量 | 直观判断还剩多少 token 容量 |
| `/status` | 显示完整运行状态 | 版本号、当前模型、账户、API 连接状态、工具可用性 |
| `/usage` | 显示 token 消耗成本、计划用量和活动统计 | 掌握花费，控制预算 |
| `/diff` | 查看未提交的文件更改及每轮对话代码差异 | 审查 Claude 做了哪些修改 |
| `/tasks` | 查看和管理所有后台运行中的代理/任务 | 支持查看详情、终止任务 |
| `/workflows` | 浏览运行中和已完成的协作工作流 | 多代理编排的进度面板 |
| `/stickers` | 订购 Claude Code 实体贴纸 | — |
| `/mobile` | 显示 QR 码下载 Claude 移动端应用 | — |
| `/release-notes` | 查看各版本更新说明 | 了解新功能与修复 |
| `/ide` | 管理 VS Code / JetBrains IDE 集成状态 | 查看连接、启停集成 |
| `/terminal-setup` | 检查终端环境配置 | 确认 Shift+Enter 换行等设置正确 |

### 2.2 常用示例

```bash
# 会话开始时快速确认环境状态
/status

# 上下文使用过半时检查容量
/context

# 审查 Claude 本轮改了什么
/diff

# 查看后台工作流进度
/workflows

# 监控 token 消耗
/usage
```

---

## 3. 配置与个性化

调整 Claude Code 的行为、模型、权限、插件和快捷键——让工具适配你的工作流。

### 3.1 核心设置

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/config` | 打开 settings.json / settings.local.json | 所有配置项的入口 |
| `/model` | 设置当前 AI 模型 | Opus（最强）、Sonnet（均衡）、Haiku（最快） |
| `/permissions` | 管理工具的 allow / deny 规则 | 按目录或工具类型设置权限 |
| `/hooks` | 查看工具事件前后的 Hook 配置 | 在特定工具调用前后自动执行脚本 |
| `/keybindings` | 打开 keybindings.json 自定义快捷键 | 支持组合键和和弦绑定 |
| `/plan` | 启用计划模式 | AI 先展示执行计划，确认后再动手 |
| `/fast` | 切换快速模式 | 使用 Opus 模型但输出更快 |
| `/effort` | 设置 AI 努力级别 | 影响分析深度和 token 消耗 |
| `/goal` | 设定任务目标 | Claude 在结束前自动检查是否达标 |
| `/doctor` | 诊断安装和配置问题 | 自动检测并输出修复建议 |

### 3.2 插件与技能

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/plugin` | 管理插件：安装、启用、禁用、卸载 | 扩展 Claude Code 功能 |
| `/reload-plugins` | 激活待处理的插件更改 | 修改插件配置后无需重启 |
| `/reload-skills` | 重新扫描磁盘上的技能文件 | 新增或修改 Skill 后使用 |
| `/skills` | 列出所有可用技能及简介 | 了解 Claude Code 能做什么 |

### 3.3 环境与集成

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/mcp` | 管理 MCP 服务器连接 | 增减外部工具和数据源 |
| `/add-dir` | 添加额外的工作目录 | 让 Claude 访问多个项目 |
| `/agents` | 管理自定义代理配置 | 名称、模型、系统提示等 |
| `/memory` | 在编辑器中打开持久化记忆文件 | 存放偏好和项目信息，跨会话生效 |
| `/powerup` | 通过交互式教程快速了解功能 | 新手入门首选 |

### 3.4 常用示例

```bash
# 切换模型
/model

# 开启计划模式，让 AI 先规划再执行
/plan

# 为当前项目添加只读权限
/permissions

# 诊断环境问题
/doctor

# 查看已安装的 Skills
/skills

# 打开快捷键配置
/keybindings

# 添加第二个工作目录
/add-dir
```

---

## 4. 账户管理

登录与登出 Anthropic 账户。

| 命令 | 功能描述 |
|------|----------|
| `/login` | 使用 Anthropic 账户登录 Claude Code |
| `/logout` | 退出当前登录状态 |

```bash
# 首次使用
/login

# 切换账户
/logout
/login
```

---

## 5. 代码开发

与代码变更直接相关的命令——审查、调试、验证、简化、初始化。

### 5.1 代码质量

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/code-review` | 审查当前 diff 的正确性缺陷和优化机会 | 支持 `low` / `medium` / `high` / `max` 四个努力级别 |
| `/review` | 审查 GitHub Pull Request | 在 PR 分支上使用 |
| `/security-review` | 对当前分支待提交更改进行安全审查 | 上线前必做 |
| `/simplify` | 审查可重用性、简化、效率和架构优化 | 仅关注代码质量，不找 bug（找 bug 用 `/code-review`） |
| `/verify` | 通过实际运行验证代码更改是否生效 | 确认修复或新功能可用 |

### 5.2 项目操作

| 命令 | 功能描述 | 用法提示 |
|------|----------|----------|
| `/init` | 初始化项目根目录下的 CLAUDE.md | 记录项目结构、技术栈、编码约定 |
| `/run` | 启动并驱动项目应用 | 观察更改在真实环境中是否生效 |
| `/debug` | 启用当前会话的调试日志 | 诊断 Claude 行为异常时使用 |

### 5.3 完整开发流程

```bash
# 第一步：初始化项目文档
/init

# 第二步：开发中随时查看差异
/diff

# 第三步：提交前进行代码审查
/code-review medium

# 第四步：运行应用确认效果
/run

# 第五步：上线前安全审查
/security-review

# 第六步（可选）：代码优化
/simplify
```

---

## 6. 高级功能与技能

这些命令背后是强大的 **Skill（技能）** 引擎，由多个 AI 代理协作完成大规模、复杂的任务。

### 6.1 大规模工程

| 命令 | 功能描述 |
|------|----------|
| `/batch` | 大规模并行变更——研究规划 → 拆分为独立任务 → 5-30 个隔离工作树代理并行执行 → 每个代理独立开 PR |
| `/embedded-c-coding` | 嵌入式 C 编码规范 Skill——强制 OOP 设计、内存安全、线程安全、硬件交互规则，修改后自动触发安全审查 |

### 6.2 深度研究与分析

| 命令 | 功能描述 |
|------|----------|
| `/deep-research` | 深度研究引擎——多源网络搜索 → 获取原文 → 对抗性交叉验证 → 生成带完整引用的综合报告 |
| `/claude-api` | Claude API / Anthropic SDK 完整参考——模型 ID、定价、参数、流式传输、工具使用、MCP、缓存、token 计数、模型迁移 |
| `/insights` | 生成 Claude Code 使用分析报告——工作模式、高频操作、效率统计 |

### 6.3 自动化与配置

| 命令 | 功能描述 |
|------|----------|
| `/loop` | 以固定间隔循环执行命令（如 `/loop 5m /code-review`，默认 10 分钟） |
| `/update-config` | 通过 settings.json 配置自动化行为（Hook）、权限规则、环境变量 |
| `/fewer-permission-prompts` | 扫描历史记录，将常见只读命令自动加入允许列表，减少权限弹窗 |
| `/statusline` | 设置和自定义终端状态栏 UI 显示内容 |
| `/team-onboarding` | 基于你的实际使用记录生成团队上手指南 |
| `/run-skill-generator` | 创建或优化项目专属的 `run-<unit>` 技能——告诉代理如何构建、启动和驱动你的项目 |

### 6.4 其他

| 命令 | 功能描述 |
|------|----------|
| `/feedback` | 提交产品反馈、报告 bug 或分享当前对话给 Anthropic 团队 |

> **注：** `/memory`（记忆文件）和 `/powerup`（交互式入门）虽在菜单中与 Skills 并列显示，但功能属于基础配置与学习范畴，已在 **第 3 章 配置与个性化** 中收录。

### 6.5 常用示例

```bash
# 深度调研一个技术方案
/deep-research "微服务架构中分布式事务的最佳实践"

# 每 5 分钟自动运行一次代码审查
/loop 5m /code-review low

# 查看 API 最新定价
/claude-api

# 生成团队培训材料
/team-onboarding
```

---

## 7. 常用工作流组合

### 场景一：日常开发

```bash
/resume                          # 恢复上次会话
/diff                            # 审查 Claude 做的修改
/code-review low                 # 快速代码审查
/verify                          # 运行应用确认功能
```

### 场景二：Pull Request 审查

```bash
/review                          # 审查 PR 代码
/security-review                 # 并行安全审查
/simplify                        # 提出优化建议
```

### 场景三：新项目上手

```bash
/init                            # 生成项目文档
/add-dir                         # 添加工作目录
/config                          # 定制项目级配置
/skills                          # 确认可用技能
```

### 场景四：深度调研

```bash
/deep-research "某技术方案的最优实现"  # 多源研究
/claude-api                            # 查阅 API 能力
/export                                # 导出研究报告
```

### 场景五：长时间任务

```bash
/fork "处理数据迁移脚本"           # 派生后台代理
/background                       # 主会话退到后台
/tasks                            # 监控后台任务状态
/workflows                        # 查看工作流进度
/usage                            # 关注 token 消耗
```

### 场景六：问题排查

```bash
/doctor                           # 诊断环境
/debug                            # 开启调试日志
/status                           # 检查连接状态
/feedback                         # 提交 bug 报告
```

---

## 8. 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + C` | 中断当前操作 |
| `Shift + Enter` | 换行输入（Windows Terminal 原生支持） |
| `↑ / ↓` | 浏览历史命令 |
| `Ctrl + R` | 搜索历史命令 |
| `Ctrl + L` | 清屏 |

> 使用 `/keybindings` 可打开配置文件进行自定义绑定，支持组合键和和弦快捷键。

---

## 附录：按字母顺序快速检索

| 命令 | 章节 | 命令 | 章节 | 命令 | 章节 |
|------|------|------|------|------|------|
| `/add-dir` | §3 | `/help` | §1 | `/rename` | §1 |
| `/agents` | §3 | `/hooks` | §3 | `/resume` | §1 |
| `/background` | §1 | `/ide` | §2 | `/review` | §5 |
| `/batch` | §6 | `/init` | §5 | `/rewind` | §1 |
| `/branch` | §1 | `/insights` | §6 | `/run` | §5 |
| `/btw` | §1 | `/keybindings` | §3 | `/run-skill-generator` | §6 |
| `/claude-api` | §6 | `/login` | §4 | `/security-review` | §5 |
| `/clear` | §1 | `/logout` | §4 | `/simplify` | §5 |
| `/code-review` | §5 | `/loop` | §6 | `/skills` | §3 |
| `/color` | §2 | `/mcp` | §3 | `/status` | §2 |
| `/compact` | §1 | `/memory` | §3 | `/statusline` | §6 |
| `/config` | §3 | `/mobile` | §2 | `/stickers` | §2 |
| `/context` | §2 | `/model` | §3 | `/tasks` | §2 |
| `/copy` | §1 | `/permissions` | §3 | `/team-onboarding` | §6 |
| `/debug` | §5 | `/plan` | §3 | `/terminal-setup` | §2 |
| `/deep-research` | §6 | `/plugin` | §3 | `/theme` | §2 |
| `/diff` | §2 | `/powerup` | §3 | `/tui` | §2 |
| `/doctor` | §3 | `/recap` | §1 | `/update-config` | §6 |
| `/effort` | §3 | `/release-notes` | §2 | `/usage` | §2 |
| `/embedded-c-coding` | §6 | `/reload-plugins` | §3 | `/verify` | §5 |
| `/exit` | §1 | `/reload-skills` | §3 | `/workflows` | §2 |
| `/export` | §1 | `/fast` | §3 | | |
| `/feedback` | §6 | `/fewer-permission-prompts` | §6 | | |
| `/focus` | §1 | `/fork` | §1 | | |
| `/goal` | §3 | | | | |
