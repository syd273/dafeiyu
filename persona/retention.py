# -*- coding: utf-8 -*-
"""艾宾浩斯式记忆保持度（retention）

R = 重要度 × exp(-Δt / S)
- Δt：距离这条记忆发生的时间
- S：记忆强度（越重要、被复习次数越多，衰减越慢）
- 复习（再次被提起/她主动想起）→ reviews+1，曲线被拉平

层级：
- facts（名字/过敏/约定）→ 永久，R 固定 1.0
- summaries → 慢衰减（半衰期长）
- 普通记忆 → 正常衰减
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from pathlib import Path

BASE = Path(__file__).parent
STORE = BASE / "retention.json"

DAY = 86400.0
BASE_HALFLIFE_DAYS = 3.0       # 普通记忆半衰期
SUMMARY_HALFLIFE_DAYS = 30.0   # 总结半衰期

IMPORTANT_KEYWORDS = [
    "名字", "叫", "过敏", "生日", "约定", "答应", "喜欢", "讨厌", "害怕",
    "考试", "考公", "学习", "工作", "病", "发烧", "吃药", "家庭", "妈妈", "爸爸",
]
EMO_WEIGHT = {
    "开心": 1.25, "兴奋": 1.25, "担心": 1.35, "着急": 1.35,
    "难过": 1.3, "生气": 1.2, "无语": 1.0, "平静": 1.0,
}


def _load() -> dict:
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(d: dict):
    STORE.write_text(json.dumps(d, ensure_ascii=False, indent=0), encoding="utf-8")


def key_of(text: str) -> str:
    norm = re.sub(r"\s+", "", text or "")
    return hashlib.md5(norm.encode("utf-8")).hexdigest()[:16]


def importance(text: str, emo: str = "平静", kind: str = "memory") -> float:
    if kind == "fact":
        return 1.0
    t = text or ""
    score = 0.45 + min(0.25, len(t) / 240.0)
    if any(k in t for k in IMPORTANT_KEYWORDS):
        score += 0.28
    score *= EMO_WEIGHT.get(emo, 1.0)
    if kind == "summary":
        score = max(score, 0.7)
    return max(0.15, min(1.0, score))


def review(text: str):
    """复习：被再次提起或她主动想起"""
    d = _load()
    k = key_of(text)
    item = d.get(k, {"reviews": 0, "first": int(time.time())})
    item["reviews"] = int(item.get("reviews", 0)) + 1
    item["last"] = int(time.time())
    d[k] = item
    _save(d)


def reviews_of(text: str) -> int:
    return int(_load().get(key_of(text), {}).get("reviews", 0))


def retention(text: str, ts: int, emo: str = "平静", kind: str = "memory") -> float:
    """0~1 的保持度"""
    if kind == "fact":
        return 1.0
    imp = importance(text, emo, kind)
    base_half = SUMMARY_HALFLIFE_DAYS if kind == "summary" else BASE_HALFLIFE_DAYS
    rv = reviews_of(text)
    # 复习次数越多，半衰期越长（间隔效应）
    half = base_half * (1.0 + 0.6 * rv) * (0.55 + 0.9 * imp)
    age_days = max(0.0, (time.time() - ts) / DAY)
    r = imp * math.exp(-age_days / half)
    return round(max(0.08, min(1.0, r)), 3)


def annotate(items: list[dict]) -> list[dict]:
    """给记忆条目补上 retention 字段"""
    out = []
    for it in items:
        it = dict(it)
        it["retention"] = retention(it.get("view") or it.get("text", ""),
                                    int(it.get("ts") or time.time()),
                                    it.get("emo", "平静"),
                                    it.get("kind", "memory"))
        out.append(it)
    return out


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(BASE))
    demo = "阿东说他今天发烧了，对消炎药过敏"
    print("fresh:", retention(demo, int(time.time())))
    print("1 day:", retention(demo, int(time.time()) - DAY))
    print("7 days:", retention(demo, int(time.time()) - 7 * DAY))
    review(demo)
    print("after review 7d:", retention(demo, int(time.time()) - 7 * DAY))
