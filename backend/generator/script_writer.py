"""Podcast script writer — supports preset styles + custom prompts."""
import random
import re
from datetime import datetime
from typing import Optional


# ════════════════════════════════════════════════════════════════
# PRESET STYLES
# ════════════════════════════════════════════════════════════════

STYLE_PRESETS = {
    "default": {
        "name": "座机原住民",
        "desc": "天津口音，座机聊天的氛围，像老友夜谈",
        "temperature": "warm",
        "icon": "📞",
        "system_hint": "",
    },
    "news": {
        "name": "新闻播报",
        "desc": "简洁清晰，信息密度高，适合快速获取今日热点",
        "temperature": "neutral",
        "icon": "📰",
        "system_hint": "播报风格，客观简洁，信息密集。",
    },
    "analytical": {
        "name": "深度分析",
        "desc": "不只说什么，还说为什么，带观点和思考",
        "temperature": "analytical",
        "icon": "🧠",
        "system_hint": "分析风格，有观点有态度，深入浅出。",
    },
    "emotional": {
        "name": "情感叙事",
        "desc": "故事感强，把新闻当故事讲，有温度",
        "temperature": "emotional",
        "icon": "💡",
        "system_hint": "叙事风格，有画面感，像在讲一个真实的故事。",
    },
    "young": {
        "name": "年轻人说",
        "desc": "网络感强，接地气，说人话不端着",
        "temperature": "casual",
        "icon": "🔥",
        "system_hint": "年轻化表达，网络用语，但不说废话。",
    },
}

PAUSE = "[停顿 3秒]"


# ════════════════════════════════════════════════════════════════
# STYLE CONTENT TEMPLATES
# ════════════════════════════════════════════════════════════════

# ── DEFAULT: 座机原住民 ──────────────────────────────────────

D_OPENING = [
    "喂。晚上好。",
    "您听着呢吗？",
]
D_OPENING_MID = [
    "还是我。座机那位。",
    "老位置，老声音。",
]
D_CLOSING = ["晚安。", "好睡。", "就这些。晚安。"]

D_TRANSITIONS = [
    "接着往下聊。",
    "再来一条。",
    "下来说说另一件事。",
    "还有一条，也值得说说。",
]

D_PHRASE = {
    "热": lambda: f"这条挺热的，说明大家都在聊。{random.choice(['我也好奇。', '忍不住点进去看。'])}",
    "涨": lambda: f"这事关钱袋子，大家都盯着，我也一样。{random.choice(['看了好几遍。', '得持续关注。'])}",
    "政策": lambda: f"这条是官方出的，得认真看看。{random.choice(['字不少，但得耐心读。', '跟我有点关系，我仔细看了一遍。'])}",
    "天气": lambda: f"这条跟天气有关。{random.choice(['这几天正好留意着。', '出门前得看看。'])}",
}

D_ANECDOTES = {
    "天津": [
        "天津这地方，说大不大，说小不小，住久了就有感情了。",
        "我在天津长大，天津的天气有时候挺让人捉摸不透的。",
    ],
    "春天": [
        "天津的春天有时候很短，脱了羽绒服没两天就热了。",
        "春天在天津挺不容易的，经常一场风就把它吹过去了。",
    ],
    "夏天": [
        "天津的夏天潮热，闷得人喘不过气来。",
        "天津的伏天最难熬，闷在屋里跟蒸笼似的。",
    ],
    "秋天": [
        "天津的秋天是最好的季节，不冷不热，刚刚好。",
        "秋天走在天津的路上，梧桐叶一片一片落，挺安静的。",
    ],
    "冬天": [
        "天津的冬天干冷，风刮在脸上跟刀子似的。",
        "但进了屋就好了，暖气烧得热，一进门就能脱外套。",
    ],
    "美食": [
        "天津人吃东西讲究，不在于多贵，在于地道。",
        "天津人吃东西从来不糊弄，早点铺子凌晨三点就起来和面。",
    ],
    "生活": [
        "有时候慢一点不是坏事，有些东西快了就丢了。",
        "日子过得快，但有些东西不会变。",
    ],
}

# ── NEWS: 新闻播报 ────────────────────────────────────────────

N_OPENING = [
    "您好，这里是今日热点播报。",
    "各位好，这里是今日热点。",
]
N_CLOSING = ["以上就是今天的全部内容，感谢收听。", "以上就是今日热点，播报完毕。"]
N_TRANSITIONS = ["下一条。", "继续。", "还有一条。"]
N_PHRASE = {
    "热": lambda: "该话题热度较高，值得关注。",
    "涨": lambda: "相关市场反应明显，需保持关注。",
    "政策": lambda: "这是官方发布的重要信息，请留意。",
    "天气": lambda: "请注意天气变化，合理安排出行。",
}

# ── ANALYTICAL: 深度分析 ────────────────────────────────────

A_OPENING = [
    "今天咱们来深度聊聊。",
    "这条有点意思，咱们仔细说说。",
]
A_CLOSING = ["这就是今天的分析，供你参考。晚安。", "分析完了，希望对你有启发。晚安。"]
A_TRANSITIONS = ["再来看下一条。", "还有一条值得深究。", "继续。"]
A_PHRASE = {
    "热": lambda: f"这事能炒这么热，背后肯定有原因。{random.choice(['咱们来分析一下。', '值得想想为什么。'])}",
    "涨": lambda: f"涨跌背后是预期，预期背后是判断。{random.choice(['这个判断对不对，值得琢磨。', '咱们试着理一理逻辑。'])}",
    "政策": lambda: f"政策出台一定有背景，咱们把它拆开来看。{random.choice(['背后的逻辑是什么？', '对谁影响最大？'])}",
    "天气": lambda: f"天气不只是天气，它影响着出行、经济、情绪。{random.choice(['咱们从几个角度看。', '它背后还藏着什么？'])}",
}

# ── EMOTIONAL: 情感叙事 ──────────────────────────────────────

E_OPENING = [
    "今天有个事，让我想了很久。",
    "跟大家说个我今天印象最深的事。",
]
E_CLOSING = ["好了，今晚就聊到这儿，希望你听完能睡个好觉。晚安。"]
E_TRANSITIONS = ["还有一件事，也想说给你听。", "接着往下讲。"]
E_PHRASE = {
    "热": lambda: f"说实话，我看到这条的时候，第一反应是：{random.choice(['大家都在聊，到底值不值得？', '这事儿我看了好几遍，有点意思。'])}",
    "涨": lambda: f"数字涨跌冷冰冰，但这背后是一个个真实的人。{random.choice(['有人在担心，有人在期待。', '我想把这件事背后的人带出来说给你听。'])}",
    "政策": lambda: f"政策文件很长，但落到每个人身上，就是日子。{random.choice(['今天咱们不讲文件，讲日子。', '我试着把它翻译成人话。'])}",
    "天气": lambda: f"天气不只是温度，它决定了今天你穿什么、出门想不想带伞、心情好不好。{random.choice(['你有没有这种感觉？', '今天我特别有感触。'])}",
}

# ── YOUNG: 年轻人说 ──────────────────────────────────────────

Y_OPENING = [
    "Yo，我又来了。",
    "yo yo yo，晚上好。",
]
Y_OPENING_MID = [
    "今天热搜上有点东西，来跟你们掰扯掰扯。",
    "这条我必须得说说。",
]
Y_CLOSING = [
    "行，今天差不多了，有缘下次再聊。Peace。",
    "冲完了，晚安。",
]
Y_TRANSITIONS = [
    "别走，下一条更重量级。",
    "继续。",
    "还有，划走就亏了。",
]
Y_PHRASE = {
    "热": lambda: f"这事直接给我整上热搜了，{random.choice(['属实没想到。', '确实有点离谱。'])}",
    "涨": lambda: f"我的建议是：{random.choice(['先别急，让子弹飞一会儿。', '稳住，别慌。'])}",
    "政策": lambda: f"说真的，这种政策文件我建议你们自己去看看原文，{random.choice(['比我讲的清楚。', '比我讲得全。'])}",
    "天气": lambda: f"出门记得看天，{random.choice(['别被淋了。', '别穿多了热死。'])}",
}

STYLE_CONTENT = {
    "default": {
        "opening": D_OPENING,
        "opening_mid": D_OPENING_MID,
        "closing": D_CLOSING,
        "transitions": D_TRANSITIONS,
        "phrase": D_PHRASE,
        "anecdotes": D_ANECDOTES,
    },
    "news": {
        "opening": N_OPENING,
        "opening_mid": ["以下是今日热点。"],
        "closing": N_CLOSING,
        "transitions": N_TRANSITIONS,
        "phrase": N_PHRASE,
        "anecdotes": {},
    },
    "analytical": {
        "opening": A_OPENING,
        "opening_mid": ["不只说是什么，更想说为什么。"],
        "closing": A_CLOSING,
        "transitions": A_TRANSITIONS,
        "phrase": A_PHRASE,
        "anecdotes": {},
    },
    "emotional": {
        "opening": E_OPENING,
        "opening_mid": ["今天印象最深的是这条。"],
        "closing": E_CLOSING,
        "transitions": E_TRANSITIONS,
        "phrase": E_PHRASE,
        "anecdotes": {},
    },
    "young": {
        "opening": Y_OPENING,
        "opening_mid": Y_OPENING_MID,
        "closing": Y_CLOSING,
        "transitions": Y_TRANSITIONS,
        "phrase": Y_PHRASE,
        "anecdotes": {},
    },
}


# ════════════════════════════════════════════════════════════════
# SCRIPT WRITER
# ════════════════════════════════════════════════════════════════

class ScriptWriter:
    """Generate podcast script with preset styles or custom prompts."""

    PRESETS = STYLE_PRESETS

    def __init__(self, style: str = "default", custom_prompt: str = ""):
        self.style = style
        self.custom_prompt = custom_prompt.strip()
        self._date = ""
        self._weekday = ""

    @property
    def is_default(self) -> bool:
        """True when using the built-in default style with no custom prompt."""
        return self.style == "default" and not self.custom_prompt

    def generate(self, date: str, hotlist: list[dict], summary: str = "") -> str:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        self._date = date_obj.strftime("%Y年%m月%d号")
        self._weekday = ["星期一", "星期二", "星期三",
                         "星期四", "星期五", "星期六", "星期日"][date_obj.weekday()]

        if self.custom_prompt:
            return self._generate_custom(hotlist)
        elif self.style == "default":
            return self._generate_default(hotlist)
        elif self.style == "news":
            return self._generate_news(hotlist)
        elif self.style == "analytical":
            return self._generate_analytical(hotlist)
        elif self.style == "emotional":
            return self._generate_emotional(hotlist)
        elif self.style == "young":
            return self._generate_young(hotlist)
        else:
            return self._generate_default(hotlist)

    # ── DEFAULT ───────────────────────────────────────────────

    def _generate_default(self, hotlist: list[dict]) -> str:
        sc = STYLE_CONTENT["default"]
        parts = []
        parts += self._header(sc)
        parts += self._overview(hotlist, sc)
        if hotlist:
            items = hotlist[:8]
            for i, item in enumerate(items):
                parts += self._item_default(item, i, sc)
        parts += self._footer(sc)
        return "\n".join(parts)

    def _item_default(self, item: dict, idx: int, sc: dict) -> list[str]:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        source = item.get("source", "")
        keywords = item.get("keywords", [])
        lines = []
        lines.append(PAUSE)
        lines.append("")
        lines.append("先说第一条。" if idx == 0 else random.choice(sc["transitions"]))
        lines.append("")
        lines.append(f"—— {title} ——")
        lines.append("")
        lines.append(f"今天有条热搜，标题叫《{title}》。")
        if source:
            lines.append(f"出自{source}。")
        if summary:
            for sent in self._split(summary)[:2]:
                ph = self._phrase_ref(sent, sc)
                if ph:
                    lines.append(ph)
                else:
                    lines.append(sent)
        anecdote = self._pick_anecdote(keywords, sc)
        if anecdote:
            lines.append("")
            lines.append(anecdote)
        lines.append("")
        return lines

    def _pick_anecdote(self, keywords: list[str], sc: dict) -> Optional[str]:
        anecdotes = sc.get("anecdotes", {})
        if not anecdotes:
            return None
        for kw in keywords:
            for key, texts in anecdotes.items():
                if key in kw:
                    return random.choice(texts)
        if random.random() < 0.3:
            flat = [t for texts in anecdotes.values() for t in texts]
            return random.choice(flat)
        return None

    # ── NEWS ─────────────────────────────────────────────────

    def _generate_news(self, hotlist: list[dict]) -> str:
        sc = STYLE_CONTENT["news"]
        parts = []
        parts += self._header(sc)
        if hotlist:
            items = hotlist[:8]
            for i, item in enumerate(items):
                parts += self._item_news(item, i, sc)
        parts += self._footer(sc)
        return "\n".join(parts)

    def _item_news(self, item: dict, idx: int, sc: dict) -> list[str]:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        source = item.get("source", "")
        keywords = item.get("keywords", [])
        lines = []
        lines.append(PAUSE)
        lines.append("")
        lines.append(f"第{idx + 1}条。" if idx == 0 else random.choice(sc["transitions"]))
        lines.append("")
        lines.append(f"—— {title} ——")
        lines.append("")
        if source:
            lines.append(f"来源：{source}。")
        if summary:
            sents = self._split(summary)
            for sent in sents[:2]:
                ph = self._phrase_ref(sent, sc)
                lines.append(ph if ph else sent)
        lines.append("")
        return lines

    # ── ANALYTICAL ───────────────────────────────────────────

    def _generate_analytical(self, hotlist: list[dict]) -> str:
        sc = STYLE_CONTENT["analytical"]
        parts = []
        parts += self._header(sc)
        parts.append(f"今天一共{len(hotlist[:8])}条值得细看，咱们来理一理。")
        parts.append("")
        parts.append(PAUSE)
        parts.append("")
        if hotlist:
            items = hotlist[:6]
            for i, item in enumerate(items):
                parts += self._item_analytical(item, i, sc)
        parts += self._footer(sc)
        return "\n".join(parts)

    def _item_analytical(self, item: dict, idx: int, sc: dict) -> list[str]:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        source = item.get("source", "")
        keywords = item.get("keywords", [])
        lines = []
        lines.append(PAUSE)
        lines.append("")
        lines.append(random.choice(sc["transitions"]))
        lines.append("")
        lines.append(f"—— {title} ——")
        lines.append("")
        lines.append(f"这条热搜叫《{title}》。")
        if source:
            lines.append(f"出处：{source}。")
        if summary:
            sents = self._split(summary)
            for sent in sents[:3]:
                ph = self._phrase_ref(sent, sc)
                lines.append(ph if ph else sent)
        lines.append("")
        return lines

    # ── EMOTIONAL ────────────────────────────────────────────

    def _generate_emotional(self, hotlist: list[dict]) -> str:
        sc = STYLE_CONTENT["emotional"]
        parts = []
        parts += self._header(sc)
        parts += self._overview_emotional(hotlist, sc)
        parts.append(PAUSE)
        parts.append("")
        if hotlist:
            items = hotlist[:6]
            for i, item in enumerate(items):
                parts += self._item_emotional(item, i, sc)
        parts += self._footer(sc)
        return "\n".join(parts)

    def _item_emotional(self, item: dict, idx: int, sc: dict) -> list[str]:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        source = item.get("source", "")
        keywords = item.get("keywords", [])
        lines = []
        lines.append(PAUSE)
        lines.append("")
        lines.append(random.choice(sc["transitions"]))
        lines.append("")
        lines.append(f"—— {title} ——")
        lines.append("")
        if summary:
            sents = self._split(summary)
            for sent in sents[:2]:
                ph = self._phrase_ref(sent, sc)
                lines.append(ph if ph else sent)
        lines.append("")
        return lines

    # ── YOUNG ────────────────────────────────────────────────

    def _generate_young(self, hotlist: list[dict]) -> str:
        sc = STYLE_CONTENT["young"]
        parts = []
        parts += self._header_young(sc)
        if hotlist:
            items = hotlist[:8]
            for i, item in enumerate(items):
                parts += self._item_young(item, i, sc)
        parts += self._footer(sc)
        return "\n".join(parts)

    def _item_young(self, item: dict, idx: int, sc: dict) -> list[str]:
        title = item.get("title", "").strip()
        summary = item.get("summary", "").strip()
        source = item.get("source", "")
        keywords = item.get("keywords", [])
        lines = []
        lines.append(PAUSE)
        lines.append("")
        lines.append(f"第{idx + 1}条。" if idx == 0 else random.choice(sc["transitions"]))
        lines.append("")
        lines.append(f"—— {title} ——")
        lines.append("")
        lines.append(f"热搜上这条叫《{title}》，{source}发的。")
        if summary:
            sents = self._split(summary)
            for sent in sents[:2]:
                ph = self._phrase_ref(sent, sc)
                lines.append(ph if ph else sent)
        lines.append("")
        return lines

    # ── CUSTOM ──────────────────────────────────────────────

    def _generate_custom(self, hotlist: list[dict]) -> str:
        """Use the custom prompt to rewrite a simple base script."""
        base = self._generate_news(hotlist)
        lines = []
        lines.append(f"# 风格提示词：{self.custom_prompt}")
        lines.append("")
        lines.append(base)
        return "\n".join(lines)

    # ── SHARED HELPERS ──────────────────────────────────────

    def _header(self, sc: dict) -> list[str]:
        opening_mid = sc.get("opening_mid", [""])
        return [
            "=" * 60,
            "",
            PAUSE,
            "",
            random.choice(sc["opening"]),
            random.choice(opening_mid) if opening_mid else "",
            "",
            f"今天是{self._date}，{self._weekday}。",
            "",
        ]

    def _header_young(self, sc: dict) -> list[str]:
        opening_mid = sc.get("opening_mid", [""])
        return [
            "=" * 60,
            "",
            PAUSE,
            "",
            random.choice(sc["opening"]),
            random.choice(opening_mid),
            "",
        ]

    def _overview(self, hotlist: list[dict], sc: dict) -> list[str]:
        if not hotlist:
            return ["今天暂时没有新的热点数据，咱们改天再聊。", ""]
        top3 = hotlist[:3]
        overview = "、".join(f"《{i.get('title', '')[:15]}》" for i in top3)
        return [
            f"今天有几条想跟你聊的，{overview}。",
            "不着急，慢慢说。",
            "",
            PAUSE,
            "",
        ]

    def _overview_emotional(self, hotlist: list[dict], sc: dict) -> list[str]:
        if not hotlist:
            return ["今天没有新数据，改天再聊。", ""]
        top = hotlist[0]
        return [
            f"今天让我印象最深的是这条：《{top.get('title', '')}》。",
            "我想把这个说给你听。",
            "",
        ]

    def _footer(self, sc: dict) -> list[str]:
        closing = sc.get("closing", ["晚安。"])
        return [
            PAUSE,
            "",
            "今天就聊到这儿。",
            "",
            random.choice(closing) if isinstance(closing, list) else closing,
            "",
            "=" * 60,
        ]

    def _phrase_ref(self, text: str, sc: dict) -> Optional[str]:
        phrase_map = sc.get("phrase", {})
        for key, fn in phrase_map.items():
            if key in text:
                return fn()
        return None

    def _split(self, text: str) -> list[str]:
        parts = re.split(r'([。！？；])', text)
        sents = []
        for i in range(0, len(parts) - 1, 2):
            sent = (parts[i] + parts[i + 1]).strip()
            if sent:
                sents.append(sent)
        if len(parts) % 2 == 1:
            last = parts[-1].strip()
            if last:
                sents.append(last)
        return sents


# ── Singleton for backward compatibility ──────────────────────

def _make_default_writer() -> ScriptWriter:
    return ScriptWriter(style="default")


def generate_default_script(date: str, hotlist: list[dict], summary: str = "") -> str:
    return _make_default_writer().generate(date, hotlist, summary)
