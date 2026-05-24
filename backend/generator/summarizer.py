"""Summary document generator."""
from datetime import datetime
from typing import Optional


class SummaryGenerator:
    """Generate daily hot news summary in Markdown format."""

    def generate(self, date: str, hotlist: list[dict]) -> str:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_display = date_obj.strftime("%Y年%m月%d日")

        weekday_map = {
            0: "星期一", 1: "星期二", 2: "星期三",
            3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日",
        }
        weekday = weekday_map.get(date_obj.weekday(), "")

        lines = []
        lines.append(f"# {date_display} 每日热点总结")
        lines.append(f"")
        lines.append(f"**日期**: {date_display} {weekday}")
        lines.append(f"**热点数量**: {len(hotlist)} 条")
        lines.append(f"")
        lines.append("---")
        lines.append("")

        # ── Section 1: Overview ──────────────────────────────
        lines.append("## 一、今日热点概览")
        lines.append("")
        lines.append("| 排名 | 标题 | 来源 | 热度 | 标签 |")
        lines.append("|------|------|------|------|------|")
        for item in hotlist:
            rank = item.get("rank", "")
            title = item.get("title", "")[:40]
            source = item.get("source", "")
            score = item.get("heat_score", 0)
            score_display = f"{score:,}" if score else "-"
            keywords = ", ".join(item.get("keywords", [])[:3])
            lines.append(f"| {rank} | {title} | {source} | {score_display} | {keywords} |")
        lines.append("")
        lines.append("---")
        lines.append("")

        # ── Section 2: Detail ────────────────────────────────
        lines.append("## 二、热点事件详情")
        lines.append("")

        for item in hotlist:
            title = item.get("title", "")
            rank = item.get("rank", "")
            source = item.get("source", "")
            source_url = item.get("source_url", "")
            publish_time = item.get("publish_time", "")
            summary = item.get("summary", "")
            keywords = item.get("keywords", [])
            background = item.get("background", "")
            related_figures = item.get("related_figures", "")
            latest_progress = item.get("latest_progress", "")
            potential_impact = item.get("potential_impact", "")

            lines.append(f"### {rank}. {title}")
            lines.append("")
            lines.append(f"**来源**: [{source}]({source_url})")
            if publish_time:
                lines.append(f"**发布时间**: {publish_time[:16]}")
            lines.append("")
            lines.append(f"**摘要**: {summary}")
            lines.append("")

            if keywords:
                tags_str = "、".join(keywords)
                lines.append(f"**标签**: {tags_str}")
                lines.append("")

            if background:
                lines.append(f"**事件背景**: {background}")
            if related_figures:
                lines.append(f"**相关人物**: {related_figures}")
            if latest_progress:
                lines.append(f"**最新进展**: {latest_progress}")
            if potential_impact:
                lines.append(f"**潜在影响**: {potential_impact}")

            lines.append("")
            lines.append("---")
            lines.append("")

        # ── Section 3: Keywords ──────────────────────────────
        lines.append("## 三、关键词标签整理")
        lines.append("")

        all_keywords = set()
        for item in hotlist:
            for kw in item.get("keywords", []):
                all_keywords.add(kw)

        if all_keywords:
            sorted_kws = sorted(all_keywords, key=lambda x: len(x))
            for kw in sorted_kws:
                lines.append(f"- **{kw}**")
        else:
            lines.append("（暂无标签数据）")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"*文档生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)
