# -*- coding: utf-8 -*-
"""Replace/add Chinese inline comments; same line count, same code values."""
import re
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "config" / "_default" / "params.yml"
lines = path.read_text(encoding="utf-8").splitlines()
assert len(lines) == 796 or len(lines) == 797, len(lines)

# Per-line Chinese comment (1-indexed); None = auto/skip blank
LINE_ZH = {}

def zh_comment_for_line(num: int, line: str) -> str:
    """Return full line with Chinese comment, preserving code."""
    s = line
    if s.strip() == "":
        return s

    # Full-line comment
    if s.lstrip().startswith("#"):
        t = s.strip()
        mapping = {
            "########################################": "########################################",
            "# Basic Configuration": "# 基础配置",
            "# main menu navigation": "# 顶部主导航菜单配置",
            "# for more icon information, please visit https://github.com/D-Sketon/hexo-theme-reimu/issues/30": "# 菜单图标说明见主题 Issue #30",
            "# 年，月，日及时间的格式化样式": "# 年、月、日及时间的格式化样式",
            "# Format style for year,month,date & time": "# Go 语言时间格式说明",
            "# subtitle: \"少女祈祷中...\"": "# 静态副标题示例（已注释）",
            "# You can also write it in the form of the following url": "# 头图也可使用完整 URL",
            "# banner: \"https://example.com\"": "# 外链头图示例（已注释）",
            "# If you want to use the srcset attribute, please enable it": "# 启用响应式头图需打开 banner_srcset",
            "# Control the display of the post cover": "# 控制文章封面显示",
            "# If not set, the banner image will be displayed by default": "# 未设置时默认使用站点头图",
            "# Its priority is lower than the cover in the Front-matter": "# 优先级低于文章 Front matter 的 cover",
            "# Control the display of the post toc": "# 控制文章目录显示",
            "# Its priority is lower than the toc in the Front-matter": "# 优先级低于文章 Front matter 的 toc",
            "# Open Graph": "# Open Graph 社交分享元数据",
            "# Content": "# 内容相关配置",
            "# Footer copyright": "# 页脚版权区域",
            "# Inject code snippet right in the footer copyright": "# 在页脚版权处注入 HTML 代码",
            "# Make sure your code snippet is safeHTML": "# 注入内容须为 safeHTML",
            "# Need help choosing? Please see...": "# 协议选择参考下方链接",
            "# https://creativecommons.org/choose/": "# CC 协议选择页",
            "# https://choosealicense.com/": "# 开源协议选择页",
            "# Sidebar": "# 侧栏配置",
            "# sidebar: right # deprecated, use sidebar.position instead": "# 已废弃：请使用 sidebar.position",
            "# Widget behavior": "# 侧栏小部件数量限制",
            "# Archive behavior": "# 归档与分类胶囊显示行为",
            "# Summary content": "# 文章摘要显示",
            "# RSS output": "# RSS 订阅输出",
            "# Sort order configuration": "# 列表排序方式配置",
            "# Available values: default, date, date-reverse, weight, weight-reverse": "# 可选值：default、date、date-reverse、weight、weight-reverse",
            "# default: hugo's default sort order for page collections, see https://gohugo.io/quick-reference/page-collections/#sort": "# default 为 Hugo 默认排序",
            "# date: sorted by date in ascending order (oldest first)": "# date 按日期升序（旧文在前）",
            "# date-reverse: sorted by date in descending order (newest first)": "# date-reverse 按日期降序（新文在前）",
            "# weight: sorted by weight in ascending order": "# weight 按权重升序",
            "# weight-reverse: sorted by weight in descending order": "# weight-reverse 按权重降序",
            "# Pagination": "# 分页条数配置",
            "# CSS": "# 样式与布局",
            "# Font loading strategy": "# 字体加载优先级策略",
            "# Custom Font -> Google Fonts -> Local FallBack Font": "# 顺序：自定义字体 → Google Fonts → 本地回退",
            "# Custom Font": "# 自定义字体",
            "# https://fonts.google.com/": "# Google Fonts 官网",
            "# Google Fonts, higher priority than local_font": "# Google Fonts 优先于 local_font",
            "# Local FallBack Font": "# 本地回退字体",
            "# Analytics": "# 访问统计",
            "# Markdown Display": "# Markdown 显示",
            "# mermaid url https://github.com/mermaid-js/mermaid": "# Mermaid 流程图项目地址",
            "# whether to expand the code block by default": "# 控制代码块默认是否展开",
            "# true means expand all code blocks by default": "# true 表示默认全部展开",
            "# false means collapse all code blocks by default": "# false 表示默认全部折叠",
            "# number means collapse the code block by default when the number of lines exceeds the specified value": "# 数字表示超过该行数则默认折叠",
            "# Clipboard configuration": "# 代码复制剪贴板文案",
            "# we need to put the configuration in an array, because hugo will automatically convert the key to lowercase": "# 配置须放数组中以防 Hugo 将键转为小写",
            "# Paragraph anchor": "# 段落锚点",
            "# Injects linkable anchor icons into paragraphs and list items in article body": "# 为正文段落和列表项注入可跳转锚点",
            "# Usage: write {#anchor-xxx} in Markdown; the matching element gets id=\"anchor-xxx\" and an anchor icon": "# 在 Markdown 中写 {#anchor-xxx} 生成锚点",
            "# Comment system": "# 评论系统",
            "# global control of the comment system": "# 评论系统全局控制",
            "# you can use multiple comment systems at the same time": "# 可同时启用多个评论系统",
            "# load order: localStorage(user manually selects) -> default": "# 加载顺序：用户选择 → default",
            "# -> valine -> waline -> twikoo -> gitalk -> giscus -> utterances -> beaudar -> disqus": "# 其后为各评论系统依次加载",
            "# comment system title": "# 评论区标题文案",
            "# valine comment system. https://valine.js.org": "# Valine 评论，见 valine.js.org",
            "# version 1.5.1": "# Valine 版本 1.5.1",
            "# notify and verify have been deprecated": "# notify 与 verify 已废弃",
            "# lang: zh-cn # deprecated, use html.lang instead": "# lang 已废弃，使用 html.lang",
            "# https://waline.js.org/": "# Waline 官网",
            "# lang: zh-CN # deprecated, use html.lang instead": "# lang 已废弃，使用 html.lang",
            "# https://twikoo.js.org": "# Twikoo 官网",
            "# https://github.com/gitalk/gitalk/blob/master/readme-cn.md": "# Gitalk 中文文档",
            "# https://giscus.app/zh-CN": "# Giscus 中文站",
            "# https://disqus.com": "# Disqus 官网",
            "# https://utteranc.es": "# Utterances 官网",
            "# https://beaudar.lipk.org/": "# Beaudar 官网",
            "# Search": "# 站内搜索",
            "# Animation": "# 动画与特效",
            "# see https://github.com/D-Sketon/aos.js": "# AOS 滚动动画库",
            "# see https://github.com/D-Sketon/mouse-firework": "# 鼠标烟花特效库",
            "# Extended features": "# 扩展功能",
            "# show the copyright below each article": "# 文章末尾显示版权卡片",
            "# Back To Top": "# 回到顶部按钮",
            "# whether to display the notification when the article is outdated": "# 文章过期时显示提醒",
            "# ICP 备案": "# 中国大陆 ICP 备案",
            "# 萌国 ICP 备案": "# 萌国 ICP 备案（icp.gov.moe）",
            "# Sponsor": "# 赞助/打赏",
            "# Share": "# 分享按钮",
            "# show categories card on home page": "# 首页显示分类卡片",
            "# Experimental features": "# 实验性功能",
            "# Inject code snippet": "# 自定义 HTML 注入点",
            "# Make sure your code snippet is safeHTML": "# 注入代码须为 safeHTML",
            "# Experimental, may have a lot of bugs, open with caution!": "# 实验功能，可能有 bug，请谨慎开启",
            "# Experimental": "# 实验性功能",
            "# https://github.com/GoogleChromeLabs/quicklink": "# Quicklink 预加载库",
            "# The `requestIdleCallback` timeout, in milliseconds.": "# requestIdleCallback 超时（毫秒）",
            "# Whether or not the URLs within the options.el container should be treated as high priority.": "# 是否高优先级预取链接",
            "# When true, quicklink will attempt to use the fetch() API if supported (rather than link[rel=prefetch]).": "# true 时优先使用 fetch 预取",
            "# Determine if a URL should be prefetched.": "# 判断哪些 URL 需要预取",
            "# Only support string": "# ignores 仅支持字符串",
            "# https://github.com/CodeByZach/pace": "# Pace 顶部进度条",
            "# Please turn on pjax to use this feature": "# 使用播放器建议先开启 pjax",
            "# if you enable meting, you must enable aplayer first": "# 启用 Meting 须先启用 APlayer",
            "# https://github.com/DIYgod/APlayer": "# APlayer 项目",
            "# https://github.com/metowolf/MetingJS": "# MetingJS 项目",
            "# if you want to use meting, please enable aplayer first": "# 使用 Meting 须先启用 APlayer",
            "# pangu.js": "# pangu.js 中英文空格",
            "# more information: https://github.com/vinta/pangu.js": "# pangu.js 项目说明",
            "# Theme": "# 主题色",
            "# experimental, may have a lot of bugs, open with caution!": "# Material 主题实验性功能",
            "# A dynamic color generation tool based on Google's Material You design guidelines, capable of extracting primary colors from any image and generating complete light and dark color schemes.": "# 根据头图按 Material You 规范动态生成深浅色主题",
            "# more information: https://github.com/2061360308/material-theme": "# material-theme 项目地址",
            "# notice: when you enable this feature, all the covers will be automatically added \"crossorigin\" attribute to support the dynamic color scheme": "# 开启后封面图会加 crossorigin 属性",
            "# so make sure your custom covers will not be blocked by the browser's CORS policy": "# 请确保图片服务器允许跨域",
            "# Explicit anchors": "# 显式锚点配置",
            "# Auto anchors": "# 自动锚点配置",
            "# Whether to enable explicit anchors: parse {#anchor-xxx} syntax in Markdown (default false)": "# 是否解析 Markdown 中的 {#anchor-xxx}",
            "# Anchor placeholder: the pattern used to match explicit anchors (no need to change unless it conflicts with article content)": "# 锚点匹配占位符，一般无需修改",
            "# Anchor id prefix: generated id = prefix + the xxx part inside the marker (default \"anchor-\")": "# 生成锚点 id 的前缀",
            "# Whether to enable auto anchors: automatically generate ids for direct child paragraphs, derived from text content (default false)": "# 是否为段落自动生成锚点 id",
            "# Maximum length of auto-generated anchor ids; longer ids will be truncated (only effective when auto.enable = true)": "# 自动锚点 id 的最大长度",
            "# true means that the dark mode is enabled by default": "# true 表示默认开启深色模式",
            "# false means that the dark mode is disabled by default": "# false 表示默认关闭深色模式",
            "# auto means that the dark mode is automatically switched according to the system settings": "# auto 表示跟随系统深浅色",
        }
        if t in mapping:
            indent = s[: len(s) - len(s.lstrip())]
            return indent + mapping[t]
        # twitter etc commented keys - translate inline part after #
        if t.startswith("#") and "twitter" in t or "google_plus" in t or "fb_" in t:
            return s  # keep as optional OG examples
        if t.startswith("# - ") or t.startswith("#   "):
            return s  # keep structure comments for fonts/social
        if "copyright: |-" in t or "Creative Commons" in t or "All website licensed" in t:
            return s  # HTML example block
        if t.startswith("# google:") or "twitter:" in t or "facebook:" in t:
            return re.sub(r"#\s*(\w+):", r"# \1 链接示例：", s) if False else s
        return s

    # Code line: replace or add trailing comment
    code, sep, comment = s, "", ""
    if " #" in s and not s.strip().startswith("#"):
        idx = s.index(" #")
        code, comment = s[:idx], s[idx + 1 :]
    elif re.match(r"^(\s*\S+?:)\s*(#.+)$", s):
        m = re.match(r"^(\s*\S+?:)\s*(#.+)$", s)
        code, comment = m.group(1), m.group(2)

    inline_map = {
        "default use taichi icon": "留空使用默认太极图标，可填 FontAwesome 或 iconfont 十六进制",
        "← 新增：分类板块": "导航项：分类列表页",
        "https://example.com / false / rgb": "可填 URL、false 或 rgb 纯色",
        "2020-current year": "版权栏显示的起始年份",
        "this path is relative to the css/main.css": "路径相对于 css/main.css，需向上一级找 images",
        "whether to use the images as a mask": "是否将图片作为 CSS 遮罩显示轮廓",
        "whether to show the sidebar menu button": "是否显示侧栏菜单按钮，移动端无效",
        "whether to show common sidebar": "文章页是否显示通用侧栏，移动端无效",
        "If you have hugo amounts of tags": "标签/分类很多时可设 true，仅首页显示胶囊以提升性能",
        "If you want to keep taxonomic capsule": "false 保持分类/标签胶囊原文大小写",
        "If you want to show the update time": "是否在列表和文章中显示最后更新时间",
        "'subtitle' or 'blockquote'": "摘要样式：副标题或块引用",
        "The number of recent articles": "RSS 输出最近文章数，-1 为全部",
        "output full content or description": "RSS 输出全文或仅摘要",
        "If true, add copyright to the end": "true 时在 RSS 文末附加版权声明",
        "controlled by categories_weight": "受分类 weight 字段控制排序",
        "controlled by tags_weight": "受标签 weight 字段控制排序",
        "controlled by weight": "受文章 weight 字段控制排序",
        "Number of posts per page in archive": "归档页与分类/标签页每页文章数",
        "Number of posts per page in home": "首页等列表每页文章数",
        "the max width of the main content area": "主内容区域最大宽度",
        "same as the icon in the social config": "图标名与 social 配置中一致",
        "default use '#' icon": "默认 # 锚点图标，可填图标码或 false 隐藏",
        "this path is relative to the css/main.css, so it needs to go up one level": "光标图片路径相对 css/main.css",
        "whether to enable zoom for mermaid diagrams": "是否允许缩放 Mermaid 图表",
        "The number of characters when the copyright is displayed": "复制超过该字符数时附加版权声明",
        "https://creativecommons.org/licenses": "CC 协议类型链接",
        "see https://docs.mathjax.org": "MathJax 配置文档",
        "default comment system, when you enable multiple comment systems": "多评论系统并存时的默认项",
        "if you want to use valine,please set this value is true": "使用 Valine 时设为 true",
        "leancloud application app id": "LeanCloud 应用 App ID",
        "leancloud application app key": "LeanCloud 应用 App Key",
        "comment list page size": "评论列表每页条数",
        "gravatar style": "Gravatar 头像风格",
        "valine comment input placeholder": "Valine 评论框占位文字",
        "valine comment header info": "Valine 评论者信息字段",
        "whether to record the IP address": "是否记录评论者 IP",
        "whether to highlight the code blocks": "是否高亮评论中的代码",
        "whether to display the number of visitors": "是否显示访客数",
        "leancloud server url": "LeanCloud 国际版 Server URL",
        "your disqus shortname": "Disqus 站点 shortname",
        "Change this to \"Your GitHub Username": "改为你的 GitHub 用户名/评论仓库名",
        "The branch name, default is main": "存储评论的仓库分支，默认 main",
        "The term to be used to create issues": "Issue 与页面的映射方式",
        "top/bottom, comment input position": "评论输入框位置：顶部或底部",
        "asc/desc, comment order": "评论排序：asc 旧在前，desc 新在前",
        "true/false, save the theme settings": "是否将主题偏好存入 sessionStorage",
        "true/false, jump to official website": "点击加载图标是否跳转官网",
        "default use inline svg": "默认内联 SVG 加载图标，可改为图片 URL",
        "whether to rotate the icon": "加载图标是否旋转",
        "left or right": "显示在左侧或右侧",
        "The number of days after which": "超过该天数未更新则提示过期",
        "string (single-layer category)": "分类名（字符串）或多级分类（数组）",
        "empty means random cover": "封面留空则使用随机封面",
        "Inject code snippet right after <head>": "在 <head> 开始标签后注入代码",
        "Inject code snippet right before </head>": "在 </head> 结束前注入代码",
        "Inject code snippet right after <body>": "在 <body> 开始标签后注入代码",
        "Inject code snippet right before </body>": "在 </body> 结束前注入代码",
        "Inject code snippet right after <aside>": "在 <aside> 开始标签后注入代码",
        "Inject code snippet right before </aside>": "在 </aside> 结束前注入代码",
        "before_sidebar | after_sidebar | after_widget": "播放器位置选项",
        "custom api": "自定义 Meting API 地址",
        "enable pangu.js to add space": "自动在中英文之间插入空格",
        "enable material_theme to generate": "根据头图动态生成 Material 主题色",
        "true | false | auto": "true 默认深色，false 默认浅色，auto 跟随系统",
    }

    if comment:
        cbody = comment.lstrip("#").strip()
        new_c = None
        for en_key, zh in inline_map.items():
            if en_key in cbody:
                new_c = f"# {zh}"
                break
        if new_c is None and re.match(r"^[\u4e00-\u9fff]", cbody):
            new_c = comment  # already Chinese
        elif new_c is None:
            new_c = comment  # keep if unknown
        else:
            pass
        if new_c and new_c != comment:
            return f"{code.rstrip()} {new_c}"
        return s

    # No comment - add based on line content
    bare = {
        "menu:": "菜单项列表",
        "  - name: home": "首页菜单",
        '    url: ""': "链接为空表示站点根路径",
        "  - name: categories": "分类页菜单",
        '    url: "categories"': "分类页路径",
        "    icon:": "菜单图标，留空用默认",
        "  - name: archives": "归档页菜单",
        '    url: "archives"': "归档页路径",
        "  - name: about": "关于页菜单",
        '    url: "about"': "关于页路径",
        "  - name: friend": "友链页菜单",
        '    url: "friend"': "友链页路径",
        'mainSections: ["post"]': "首页文章列表使用的 content section",
        'yearFormat: "2006"': "年份显示格式",
        'monthFormat: "2006-01"': "年月显示格式",
        'dateFormat: "2006-01-02"': "日期显示格式",
        'timeFormat: "2006-01-02 15:04:05"': "日期时间显示格式",
        "author: Ounigulog": "站点作者名称",
        "email: 2144253736@qq.com": "作者联系邮箱",
        'description: "泪水打湿猪脚饭。。。"': "站点描述文字",
        "subtitle:": "首页副标题配置",
        "  typing:": "打字机效果",
        "    enable: true": "启用打字机",
        "    strings:": "轮播句子列表",
        "banner: \"images/banner.webp\"": "站点顶部头图路径",
        "banner_srcset:": "响应式头图配置",
        "  enable: false": "是否启用（本行含义视上下文而定）",
        "  srcset:": "各断点对应图片列表",
        '    - src: "images/banner-600w.webp"': "小屏头图文件",
        '      media: "(max-width: 479px)"': "超小屏媒体查询",
        '    - src: "images/banner-800w.webp"': "中屏头图文件",
        '      media: "(max-width: 799px)"': "中屏媒体查询",
        '    - src: "images/banner.webp"': "大屏头图文件",
        '      media: "(min-width: 800px)"': "大屏及以上媒体查询",
        'avatar: "sln.jpg"': "侧栏头像文件名",
        "toc: true": "全局启用文章目录",
        "open_graph:": "Open Graph 配置块",
        "  enable: true": "启用 OG 标签",
        "  options:": "OG 扩展选项",
        "excerpt_link: Read More": "列表摘要「阅读更多」文字",
        "copyright:": "自定义页脚版权 HTML",
        "footer:": "页脚配置",
        "  powered: true": "显示 Powered by 信息",
        "  count: true": "显示全站字数与阅读时间",
        "  busuanzi: true": "启用不蒜子访问统计",
        "  icon:": "页脚装饰图标",
        "    rotate: true": "图标旋转动画",
        "sidebar:": "侧栏布局",
        "  position: left": "侧栏显示在左侧",
        "  article:": "文章页侧栏选项",
        "social:": "侧栏社交链接",
        "widgets:": "侧栏小部件列表",
        "  - category": "显示分类小部件",
        "  - tag": "显示标签小部件",
        "  - tagcloud": "显示标签云",
        "  - recent_posts": "显示最近文章",
        "category_limits: 10": "侧栏最多显示分类数",
        "tag_limits: 10": "侧栏最多显示标签数",
        "recent_posts_limits: 5": "最近文章条数上限",
        "tagcloud_limits: 20": "标签云标签数上限",
        "only_show_capsule_in_index: false": "是否仅在首页显示分类/标签胶囊",
        "uppercase_capsule: true": "分类/标签胶囊是否大写",
        "show_update_time: true": "是否显示文章更新时间",
        "summary:": "摘要配置",
        "  style: 'subtitle'": "摘要展示样式",
        "rss:": "RSS 配置",
        "sort_order:": "排序配置",
        "  taxonomy:": "分类与标签页排序",
        "paginate:": "分页配置",
        "layout:": "页面布局",
        "triangle_badge:": "右上角三角徽标",
        "  enable: true": "显示三角徽标",
        "  link: https://github.com/ounigulog": "徽标点击跳转链接",
        "reimu_cursor:": "灵梦风格鼠标指针",
        "  cursor:": "各状态光标图片",
        "icon_font: 4552607_ex15nbittbh": "iconfont 项目 ID",
        "custom_font:": "自定义字体",
        "  article:": "正文字体配置",
        "  code:": "代码字体配置",
        "font:": "Google 字体",
        "local_font:": "本地回退字体",
        "dark_mode:": "深色模式",
        "baidu_analytics: false": "百度统计 ID，false 关闭",
        "google_analytics: false": "Google Analytics ID",
        "clarity: false": "Microsoft Clarity ID",
        "mermaid:": "Mermaid 图表",
        "code_block:": "代码块行为",
        "  expand: true": "代码块默认展开",
        "clipboard:": "复制提示文案",
        "  success:": "复制成功多语言文案",
        "  fail:": "复制失败多语言文案",
        "math:": "数学公式引擎",
        "  katex:": "KaTeX 配置",
        "  mathjax:": "MathJax 配置",
        "anchor:": "锚点配置",
        "  explicit:": "显式锚点",
        "  auto:": "自动锚点",
        "comment:": "评论全局",
        "  title:": "评论标题",
        "valine:": "Valine 评论",
        "waline:": "Waline 评论",
        "  emoji:": "Waline 表情包地址",
        "  meta:": "评论者可选字段",
        "  requiredMeta:": "评论必填字段",
        "twikoo:": "Twikoo 评论",
        "gitalk:": "Gitalk 评论",
        "giscus:": "Giscus 评论",
        "disqus:": "Disqus 评论",
        "utterances:": "Utterances 评论",
        "beaudar:": "Beaudar 评论",
        "algolia_search:": "Algolia 搜索",
        "  hits:": "搜索结果配置",
        "preloader:": "页面加载动画",
        "  text:": "加载提示多语言文案",
        "animation:": "AOS 入场动画",
        "  options:": "动画分区配置",
        "firework:": "鼠标烟花",
        "    particles:": "烟花粒子组",
        "article_copyright:": "文末版权卡",
        "  content:": "版权卡显示字段",
        "top:": "回到顶部",
        "outdate:": "文章过期提醒",
        "  message:": "过期提示多语言文案",
        "icp:": "ICP 备案",
        "moe_icp:": "萌国 ICP",
        "sponsor:": "赞助",
        "  tip:": "赞助提示语",
        "  qr:": "收款二维码",
        "share:": "分享平台列表",
        "home_categories:": "首页分类卡片",
        "  content:": "分类卡片内容",
        "injector:": "HTML 注入",
        "pjax:": "PJAX 无刷新",
        "quicklink:": "链接预加载",
        "service_worker:": "Service Worker",
        "live2d:": "Live2D 看板娘",
        "live2d_widgets:": "Live2D 挂件",
        "pace:": "顶部加载进度条",
        "player:": "音乐播放器",
        "  aplayer:": "APlayer 播放器",
        "  meting:": "Meting 在线歌单",
        "pangu:": "中英文自动空格",
        "material_theme:": "Material 动态主题色",
        "internal_theme:": "手动主题 CSS 变量",
        "  light:": "浅色模式变量",
        "  dark:": "深色模式变量",
    }

    stripped = s.rstrip()
    if stripped in bare:
        return f"{stripped}  # {bare[stripped]}"

    # list items typing strings
    if stripped.startswith("- ") and "http" not in stripped and "#" not in stripped:
        if "本是清汤" in stripped:
            return stripped + "  # 打字机轮播句子"
        if stripped in ("- 233", "- 呃呃", "- 如此这般"):
            return stripped + "  # 打字机轮播句子"
        if "unpkg.com" in stripped or stripped.startswith("- https"):
            return stripped + "  # Waline 表情 CDN"
        if stripped in ("- nick", "- mail", "- link"):
            return stripped + "  # Waline 评论字段"
        if stripped.startswith("- Mulish") or "Noto Serif" in stripped:
            return stripped + "  # 正文字体"
        if stripped.startswith('-"') or stripped.startswith("- PingFang") or "YaHei" in stripped or stripped == "- sans-serif":
            return stripped + "  # 正文回退字体"
        if stripped in ("- Menlo", "- Monaco", "- Consolas", "- monospace"):
            return stripped + "  # 代码回退字体"

    # CSS variables
    if stripped.startswith("--"):
        return stripped + "  # 主题或代码高亮 CSS 变量"

    # animation / firework keys
    anim = {
        "post: fade-up": "首页文章卡片动画",
        "widget: fade-up": "小部件动画",
        "sidebar: fade-up": "侧栏动画",
        "whole: fade-up": "整体淡入上滑",
        "date: zoom-in": "日期缩放进入",
        "category: zoom-in": "分类缩放进入",
        "tag: zoom-in": "标签缩放进入",
        "comment: zoom-in": "评论区缩放进入",
        "reading: zoom-in": "阅读信息缩放进入",
        "nav: fade-up": "导航淡入上滑",
        "section: fade-up": "区块淡入上滑",
        "title: slide-up": "标题上滑进入",
        "subTitle: slide-down": "副标题下滑进入",
        'excludeElements: ["a", "button"]': "点击这些元素不触发烟花",
        'move: ["emit"]': "粒子发射运动",
        'move: ["diffuse"]': "粒子扩散运动",
        "easing: easeOutExpo": "缓动函数",
        "number: 20": "粒子数量",
        "duration: [1200, 1800]": "动画时长范围（毫秒）",
        "radius: [16, 32]": "粒子半径范围",
        "alpha: [0.3, 0.5]": "粒子透明度范围",
        "radius: 20": "扩散圈半径",
        "alpha: [0.2, 0.5]": "扩散圈透明度",
        "lineWidth: 6": "扩散圈线宽",
        "disable_on_mobile: false": "移动端是否禁用",
    }
    if stripped in anim:
        return stripped + f"  # {anim[stripped]}"

    # i18n value lines - comment is the value itself
    if ": Leave a comment" in stripped or ": 说些什么" in stripped or "コメント" in stripped or "Deixe um" in stripped:
        return stripped + "  # 评论标题文案"
    if stripped.startswith("zh-CN:") or stripped.startswith("en:") or stripped.startswith("ja:"):
        if "少女" in stripped or "Loading" in stripped or "Carregando" in stripped:
            return stripped + "  # 加载屏提示文字"
        if "复制" in stripped or "Copy " in stripped or "コピー" in stripped or "Copiado" in stripped:
            return stripped + "  # 复制按钮提示"
        if "咖啡" in stripped or "coffee" in stripped or "コーヒー" in stripped or "café" in stripped:
            return stripped + "  # 赞助提示语"
        if "最后更新" in stripped or "last updated" in stripped or "更新日" in stripped or "atualizado" in stripped:
            return stripped + "  # 文章过期提示"

    # mathjax json - keep structure, short comment
    if "tags:" in stripped or "inlineMath" in stripped or "displayMath" in stripped:
        return stripped + "  # MathJax 配置项"
    if "skipHtmlTags" in stripped or "ignoreHtmlClass" in stripped or "processHtmlClass" in stripped:
        return stripped + "  # MathJax 渲染选项"
    if stripped.strip() in ("[", "]", "{", "}", "],", "},"):
        return stripped  # structural
    if "loader:" in stripped or "autoload:" in stripped or "packages:" in stripped:
        return stripped + "  # MathJax 加载配置"

    return s


out = [zh_comment_for_line(i + 1, line) for i, line in enumerate(lines)]
result = "\n".join(out) + "\n"
path.write_text(result, encoding="utf-8", newline="\n")
print(len(out), "lines written")
