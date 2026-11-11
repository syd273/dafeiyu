# -*- coding: utf-8 -*-
"""任务路由：简单任务优先交给本地 qwen3.5:9b，复杂任务交给 DeepSeek 云端。

判定维度：
- 任务类型（主动消息/分享配文/说说/闲聊 → 简单）
- 文本长度与复杂度关键词（为什么/怎么办/计划/情绪困扰等 → 复杂）
"""

from __future__ import annotations

# 复杂信号：出现这些就交给云端
COMPLEX_WORDS = [
    "为什么", "怎么办", "怎么处理", "计划", "未来", "打算", "建议", "分析",
    "解释", "原理", "工作", "考试", "学习", "面试", "论文", "代码", "报错",
    "难过", "哭", "失眠", "焦虑", "压力", "分手", "吵架", "生病", "发烧",
    "医院", "吃药", "难受", "委屈", "想放弃", "迷茫",
    "重写", "总结", "概括", "复盘", "记忆", "梳理", "写一段", "生成", "翻译",
]
# 简单任务类型（直接本地）
SIMPLE_KINDS = {"proactive", "share", "feed", "greeting", "short_reply"}


def is_simple(text: str, kind: str = "chat") -> bool:
    if kind in SIMPLE_KINDS:
        return True
    t = (text or "").strip()
    if len(t) <= 12:
        return True
    if len(t) >= 60:
        return False
    if any(w in t for w in COMPLEX_WORDS):
        return False
    # 多个问号/多句话视为复杂
    if t.count("？") + t.count("?") >= 2 or t.count("。") >= 3:
        return False
    return True


def pick_provider(text: str, kind: str = "chat") -> str:
    """返回 'local' 或 'cloud'"""
    return "local" if is_simple(text, kind) else "cloud"
