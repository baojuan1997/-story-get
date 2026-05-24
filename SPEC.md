# 《"误"联网原住民》播客助手 — 项目规范

## 1. 项目概述

**项目名称**: Podcast Daily Hot
**项目类型**: 全栈新闻播客自动化生成系统
**核心功能**: 每日自动抓取热点新闻 → 生成播客文字稿 → TTS语音合成 → Web可视化展示
**目标用户**: 播客主播（22岁天津物联网专业背景，深夜陪伴风格）

---

## 2. 功能模块划分

```
story_get/
├── backend/                  # Python FastAPI 后端
│   ├── main.py               # FastAPI 入口
│   ├── scraper/              # 新闻抓取模块
│   │   ├── __init__.py
│   │   ├── sina_news.py      # 新浪新闻
│   │   ├── tencent_news.py   # 腾讯新闻
│   │   ├── weibo_hot.py      # 微博热搜
│   │   └── base.py           # 基类
│   ├── generator/            # 内容生成模块
│   │   ├── __init__.py
│   │   ├── summarizer.py     # 热点总结生成
│   │   └── script_writer.py  # 播客文字稿生成（天津风格）
│   ├── tts/                  # TTS 模块
│   │   ├── __init__.py
│   │   └── tts_service.py     # 语音合成服务
│   ├── storage/              # 数据存储
│   │   ├── __init__.py
│   │   └── data_store.py     # JSON文件存储
│   ├── scheduler/             # 定时任务
│   │   ├── __init__.py
│   │   └── daily_task.py     # 每日定时任务
│   └── routers/
│       ├── __init__.py
│       ├── hotlist.py         # 热点列表API
│       ├── summary.py         # 总结文档API
│       └── audio.py           # 音频API
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── api/              # API 调用
│   │   ├── views/             # 页面视图
│   │   └── components/        # 组件
│   └── package.json
├── data/                      # 数据存储目录
│   ├── hotlist/               # 热点JSON
│   ├── summary/               # 总结文档MD
│   ├── script/                # 文字稿MD
│   └── audio/                 # MP3音频
├── requirements.txt
├── SPEC.md
└── README.md
```

---

## 3. 视觉与界面规范

### 3.1 配色方案
- 主色: `#FF6B9D`（粉红色，呼应座机电话主题）
- 深色背景: `#0D0D0D`（深夜主题）
- 次背景: `#1A1A2E`（卡片背景）
- 强调色: `#FFB347`（橙色热度标签）
- 文字色: `#E8E8E8`
- 副文字: `#9999AA`
- 边框: `#2A2A3E`

### 3.2 字体
- 主字体: `"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif`
- 等宽字体（代码/时间戳）: `"JetBrains Mono", monospace`

### 3.3 热搜榜界面
- 类似微博热搜列表，每条带排名序号
- 右侧显示热度数值或标签
- 点击展开详情面板（侧滑或弹窗）
- 顶部日期选择器 + 刷新按钮
- 夜间深色主题

### 3.4 详情面板
- 标题 + 标签
- 来源 + 发布时间
- 摘要 / 详细内容
- 相关事件（可跳转）
- 生成的文字稿展示
- 下载按钮（总结文档 / 音频MP3）

---

## 4. 数据结构规范

### 4.1 热点条目 (HotItem)
```json
{
  "id": "2026-05-18_001",
  "date": "2026-05-18",
  "rank": 1,
  "title": "标题",
  "source": "新浪新闻",
  "source_url": "https://...",
  "publish_time": "2026-05-18T10:30:00",
  "summary": "50-100字摘要",
  "keywords": ["标签1", "标签2"],
  "heat_score": 985600,
  "content": "详细内容（可选）"
}
```

### 4.2 总结文档 (DailySummary)
```markdown
# 2026-05-18 每日热点总结

## 概览
[TOP20热点列表]

## 事件一：标题
- **背景**: ...
- **相关人物**: ...
- **最新进展**: ...
- **潜在影响**: ...
- **标签**: [标签1, 标签2]
```

### 4.3 播客文字稿 (PodcastScript)
```markdown
# 2026-05-18 播客文字稿

## 开篇
拿起座机...

## 正文
[各热点分段播报]

## 结尾
搁下电话...
```

---

## 5. API 设计

### 5.1 热点相关
- `GET /api/hotlist?date=YYYY-MM-DD` — 获取当日热点列表
- `GET /api/hotlist/{item_id}` — 获取单条热点详情
- `POST /api/hotlist/refresh` — 手动触发抓取

### 5.2 文档相关
- `GET /api/summary/{date}` — 获取总结文档
- `GET /api/script/{date}` — 获取文字稿
- `GET /api/audio/{date}` — 获取音频文件

### 5.3 调度相关
- `POST /api/scheduler/trigger` — 触发每日生成任务

---

## 6. 播客风格规范（天津物联网主播）

### 开篇
```
"喂。晚上好。还是我。座机那位。"

"今天是2026年5月18号，星期一。咱们来聊聊今天都发生了些什么。"

"不着急，慢慢说。您就当我是您床头那台路由器，蓝灯一闪一闪的那种。"
```

### 正文
- 每条热点前加过渡语："下来说说..." "再来一条..."
- 事件之间用停顿标记 "[停顿]"
- 用物联网专业概念做比喻
- 天津话点缀词：嘛、害、咱、您
- 不煽情，只陈述事实和感受

### 结尾
```
"行了。今天就聊到这儿。"

"您要是觉得还行，就当个心跳包，时不时回来看看。"

"闭眼吧。晚安。"

[搁下电话音效]
```

### 文字稿输出格式
```
[拿起座机音效]

喂。晚上好。还是我。座机那位。

今天是2026年5月18号，星期一。咱们来聊聊今天都发生了些什么。

[停顿]

下来说说今天的第一条。

[过渡]


---
**事件一：XXX事件**
这条说的是……（事件概述）

[停顿]

下来说说第二条……

---

[搁下座机音效]

行了。闭眼吧。晚安。
```

---

## 7. TTS 配置

- 使用 Azure TTS 或 Edge TTS（免费）
- 语音：中文女声，语速 0.9（偏慢）
- 输出格式：MP3，44.1kHz
- 文件命名：`{date}_podcast.mp3`

---

## 8. 调度策略

- 每日早上 8:00 自动抓取热点并生成
- 数据存储在 `data/` 目录下，按日期归档
- 支持手动触发

---

## 9. 依赖技术

- **后端**: Python 3.10+ / FastAPI / uvicorn / httpx / beautifulsoup4
- **前端**: Vue 3 / Vite / Axios / Pinia
- **TTS**: edge-tts (免费微软Edge语音)
- **数据**: JSON文件存储 + 文件系统
- **调度**: APScheduler
