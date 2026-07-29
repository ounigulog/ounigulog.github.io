---
# ── 必填 ──
title: 'GIT'

# ── 时间（可不填，由 Git 记录自动生成）──
date: 2026-05-28
lastmod: 2026-05-28

# ── 状态 ──
draft: true

# ── 分类 & 标签 ──
categories:
  - git #分类1
  - #分类2
tags:
  - #标签1
  - #标签2

# ── 封面 & 横幅 ──
cover: /images/covers/Git-Icon-1788C.png   # 文章卡片封面图，也用于社交分享预览
banner: images/Git-Logo-White.png       # 页面顶部横幅图，设为 false 则隐藏

# ── 排序 & 置顶 ──
weight:                     # 数字越小越靠前（仅在 sort_order 为 "weight" 时生效）

# ── SEO & 摘要 ──
description: '我自己关于使用git管理项目的经验总结'       # 页面 meta description，卡片上的描述文字
keywords:                     # 页面 meta keywords
  - git#关键词1
  - #关键词2

# ── 图库 ──
photos:                       # 文章内图片画廊，会渲染在正文上方
  - /images/gallery/Git-Icon-1788C.png

# ── 功能开关（设为 false 关闭）──
copyright: false              # 显示版权声明
sponsor: false                 # 显示赞助按钮
comments: false                # 显示评论区
toc: true                    # 显示目录
math: true                 # 启用 KaTeX/MathJax 数学公式渲染
mermaid: true               # 启用 Mermaid 图表渲染
outdated: true              # 标记为过时文章，页首显示警告
---





# 参考网页

首先总结一下参考过的网站：

## Learn Git Branching

有简中翻译

讲的比较基础，动画做得很好，简明易懂。

tab键可以补全代码

还有自创命令来模拟团队合作

高级例题也很有挑战性，可能符合现实项目

但是引导做的不好，有一些命令是藏着掖着的，况且演示动画跳得很快

{{<externalLinkCard title="Learn Git Branching" link="https://learngitbranching.js.org/?locale=zh_CN" cover="auto">}}

## **Interactive Git Playground**

纯英文

纯手打，没有tab键，在网页模拟终端进行模拟

在开头有引导，用一段话告诉你目前需要什么指令

同样有动画，效果很好

打错命令会有提示

{{<externalLinkCard title="Interactive Git Playground" link="https://developwithmi.com/labs/git/" cover="auto">}}



# 个人项目git管理

**核心原则是：主分支 `main` 始终保持稳定可发布，所有实验性修改都在新分支上进行，不论验证成功或失败，都不删除已创建的分支**。

保留开发历史，又能随时回退。

## 1. 初始化（Git 跟踪项目）并配置 .gitignore

首先进入项目根目录，初始化本地仓库：

```bash
git init
```

此时会生成隐藏文件夹 `.git`，Git 开始跟踪文件变化。

**重要：在首次 `git add` 之前，必须配置 `.gitignore` 文件**，告诉 Git 忽略那些不需要版本控制的文件（如编译产物、依赖目录、操作系统临时文件等），避免它们被误提交。

**创建并编写 .gitignore：**

```bash
# 在项目根目录创建 .gitignore 文件
touch .gitignore
```

然后用任意编辑器打开 `.gitignore`，按行写入忽略规则，例如：

```bash
# 依赖目录
node_modules/
vendor/

# 编译输出
build/
dist/
*.o
*.class

# 操作系统生成文件
.DS_Store
Thumbs.db

# 环境配置文件（含敏感信息）
.env
*.log
```

- 每行一个模式，`/` 结尾表示忽略整个目录，`*` 是通配符。
- 设置完成后，可运行 `git status` 检查是否还有不想跟踪的文件出现在列表中，确认 `.gitignore` 生效。

> **提示**：推荐在项目开始时就把 `.gitignore` 提交到仓库，这样其他协作者（或你在其他设备上）也能复用这些规则。

## 2. 绑定远程仓库

先在 GitHub 创建一个空仓库（不要勾选任何初始化选项），复制仓库地址，然后绑定：

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
```

- `origin` 是远程仓库的别名，`git remote -v` 可查看绑定结果。

## 3. 提交第一个 demo 到本地仓库 main 分支

将现有代码全部纳入 Git 管理，并生成第一个快照：

```bash
git add .                    # 将所有文件添加至暂存区
git commit -m "初始提交：第一个 demo 版本"
```

- 此时，默认的 `main` 分支自动创建，并指向这个提交。
- **`main` 分支现在就代表你的首个稳定 demo**。

## 4. 创建新分支并提交到本地仓库

当需要添加新功能或进行试验时，从 `main` 创建新分支，而不是直接修改 `main`：

```bash
git checkout -b feature-demo-improve
```

- 这会在**当前 `main` 所指向的提交**处创建一个新分支 `feature-demo-improve`，并切换到它。
- 此时 `HEAD` 指向新分支，后续提交都会记录在这个分支上。

在新分支上修改代码后，提交到本地仓库：

```bash
# ……编辑文件，实现改进……
git add .
git commit -m "在 feature-demo-improve 上增强 demo 功能"
```

现在，仓库历史如下图所示（`main` 指针未移动，仍在最初的 demo 提交处）：

```
     feature-demo-improve
     ↓
A -- B   (A 是初始提交，B 是新增提交)
↑
main
```

## 5. 验证成功与失败的处理（不删除分支）

在新分支上进行充分测试，根据结果执行不同操作。

### ✅ 验证成功：将修改合并到 main

```bash
git checkout main               # 切换回 main，此时 HEAD 回到创建分支点
git merge feature-demo-improve  # 将 feature-demo-improve 的提交合并过来
```

- 因为 `main` 在分叉后无新提交，此次合并会执行**快进合并**，`main` 指针直接移动到 B。
- 合并完成后，`main` 和 `feature-demo-improve` 指向同一个提交 B，但**两个分支都保留**，满足“不删除”要求。

### ❌ 验证失败：让 HEAD 回到创建分支点，不删除分支

验证失败意味着你决定放弃这次分支上的工作，让项目状态恢复到创建分支之前（即仍停留在最初的 demo 版本）：

```bash
git checkout main
```

- 因为 `main` 指针自创建分支以来从未移动，`git checkout main` 会使 `HEAD` 重新指向 `main`，即**创建分支时的那个提交 A**。
- 工作目录的所有文件也会恢复为 A 的状态。
- 分支 `feature-demo-improve` 仍然存在于仓库中，但不会被使用，你随时可以以后再切换回去查看或继续修改。

> **注意**：这种方式适用于 `main` 在创建分支后没有新提交的情况。在本流程中，我们始终在验证成功后才向 `main` 合并，因此 `main` 总是保持着之前那个稳定版本的提交，**完全满足“回到创建分支点”的需求**。

## 6. 向远程仓库（GitHub）提交稳定版 demo

当 `main` 已经集成了你所期望的所有修改，成为一个稳定版本后，推送到 GitHub：

```bash
git push -u origin main
```

- `-u` 建立本地 `main` 与远程 `origin/main` 的追踪关系，之后只需 `git push` 即可。
- 此时 GitHub 仓库上将出现你的稳定版 demo 代码。

## 7. 再次添加新分支并提交到本地仓库

在稳定版 demo 推送后，你准备开始开发产品的下一个稳定版本（产品版）。同样从最新的 `main` 创建新分支：

```bash
git checkout -b feature-product
```

在这个分支上实现产品所需的全部功能，然后提交：

```bash
# ……大量代码修改，产品功能开发……
git add .
git commit -m "实现产品核心功能"
```

现在仓库状态：`main` 指向之前的稳定版 demo 提交，`feature-product` 指向一个新的提交 C。

```
          feature-product
          ↓
A -- B -- C
     ↑
    main
```

## 8. 验证成功与失败的处理（不删除分支）

与步骤 5 相同，只是分支名换为 `feature-product`。

### ✅ 验证成功：合并产品分支到 main

```bash
git checkout main          # HEAD 指向创建分支时的提交 B
git merge feature-product  # 将产品功能合并进来
```

- 快进合并后，`main` 指针移动至 C，`feature-product` 依然保留。

### ❌ 验证失败：HEAD 回到创建分支点

```bash
git checkout main
```

- `HEAD` 回到提交 B（即创建 `feature-product` 时的稳定 demo 版本），`feature-product` 分支不被删除，但暂时搁置。
- 此时项目代码完全恢复为稳定 demo 状态，可以重新规划产品开发方向。

## 9. 向远程仓库（GitHub）提交稳定版产品

当产品的所有功能都已整合进 `main`，并且通过验证后，再次推送：

```bash
git push
```

- 因为之前已设置追踪关系，直接推送即可。
- 现在远程仓库上就是你的**稳定版产品**。

## 完整流程回顾（命令速查）

| 步骤 | 操作                        | 关键命令                                                     |
| ---- | --------------------------- | ------------------------------------------------------------ |
| 1    | 初始化                      | `git init`                                                   |
| 2    | 绑定远程                    | `git remote add origin <url>`                                |
| 3    | 提交首个 demo               | `git add . && git commit -m "首个demo"`                      |
| 4    | 创建 demo 分支并提交        | `git checkout -b feature-demo-improve` + 修改 + `git add . && git commit -m "..."` |
| 5    | 验证成功合并 / 验证失败回退 | 成功：`git checkout main && git merge feature-demo-improve` <br> 失败：`git checkout main` |
| 6    | 推送稳定版 demo             | `git push -u origin main`                                    |
| 7    | 创建产品分支并提交          | `git checkout -b feature-product` + 修改 + `git add . && git commit -m "..."` |
| 8    | 再次验证                    | 同步骤 5，分支名换为 `feature-product`                       |
| 9    | 推送稳定版产品              | `git push`                                                   |

这个流程非常干净，保留了所有尝试过的分支作为历史记录，同时确保 `main` 始终是那个可以随时发布的稳定版本。

