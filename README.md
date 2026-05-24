# "误"联网原住民 — 播客助手

每日热点自动抓取 + 播客文字稿生成 + TTS语音合成的全栈自动化系统。
**手动触发，想哪天用哪天运行即可。**

## 功能特性

- **热点抓取**：从新浪新闻、腾讯新闻、微博热搜抓取 Top 20 热点
- **总结文档**：生成 Markdown 格式的热点总结报告
- **播客文字稿**：根据主播风格（22岁天津物联网专业毕业生）生成口语化文字稿
- **TTS语音合成**：使用 Windows 内置语音引擎，无需网络
- **Web界面**：类似微博热搜的可视化展示，支持日期切换和内容下载

## 快速开始

### 方式一：一键启动（推荐）

```bash
# 双击运行 start.bat
start.bat
```

### 方式二：手动启动

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 启动后端（端口 8765）
python -m backend.main

# 3. 新开终端，启动前端（端口 5173，需先安装 Node.js）
cd frontend && npm install && npm run dev
```

### 访问地址

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:8765/docs

## 使用方法

1. 启动服务后，打开 http://localhost:5173
2. 点击「刷新」按钮 → 系统自动完成：抓取热点 → 生成总结 → 生成文字稿 → 合成音频
3. 等待完成后，点击任意热搜条目 →「下载」标签 → 下载 `.md` 总结 / `.md` 文字稿 / `.mp3` 音频

想哪天用就哪天运行，无需每日开机。

## 目录结构

```
story get/
├── backend/
│   ├── main.py              # FastAPI 入口（端口 8765）
│   ├── pipeline.py          # 手动执行入口（抓取→总结→文字稿→TTS）
│   ├── scraper/             # 新闻抓取
│   ├── generator/           # 内容生成
│   │   ├── summarizer.py    # 热点总结生成
│   │   └── script_writer.py # 播客文字稿（天津主播风格）
│   ├── tts/                  # TTS 语音合成
│   ├── storage/              # JSON 文件存储
│   └── routers/              # REST API
├── frontend/                 # Vue3 前端
├── data/                     # 数据输出目录
│   ├── hotlist/             # YYYY-MM-DD_hotlist.json
│   ├── summary/             # YYYY-MM-DD_summary.md
│   ├── script/              # YYYY-MM-DD_script.md
│   └── audio/               # YYYY-MM-DD_podcast.mp3
├── requirements.txt
├── start.bat
└── README.md
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Axios |
| 后端 | Python 3.10+ / FastAPI / uvicorn |
| 抓取 | httpx + BeautifulSoup |
| TTS | pyttsx3（Windows 内置语音，离线工作） |
| 存储 | JSON 文件 + 文件系统 |

## 注意事项

- 热点抓取依赖网络连接
- TTS 使用 Windows 内置语音，无需网络
- 数据存储在 `data/` 目录下，可定期备份
- 刷新一次生成当日所有内容，可重复刷新重新生成
