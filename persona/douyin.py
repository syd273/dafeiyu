# -*- coding: utf-8 -*-
"""抖音：抓热榜（无需登录），给安诗鱼提供“自己刷抖音”的素材。"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from urllib.parse import quote

import requests

BASE = Path(__file__).parent
CACHE = BASE / ".douyin_cache.json"
CACHE_TTL = 1800

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
}


def _fetch() -> list[dict]:
    try:
        s = requests.Session()
        s.trust_env = False
        r = s.get("https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/",
                  headers=HEADERS, timeout=20)
        data = r.json()
        words = data.get("word_list") or ((data.get("data") or {}).get("word_list") or [])
        out = []
        for w in words:
            word = (w.get("word") or "").strip()
            if not word:
                continue
            cover = ""
            try:
                cover = (w.get("word_cover") or {}).get("url_list", [""])[0]
            except Exception:
                pass
            out.append({
                "title": word,
                "hot": w.get("hot_value") or 0,
                "url": "https://www.douyin.com/search/" + quote(word),
                "cover": cover,
            })
        return out
    except Exception:
        return []


def items(force: bool = False) -> list[dict]:
    if not force and CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    out = _fetch()
    if out:
        try:
            CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    return out


def random_hot() -> dict | None:
    xs = items()
    if not xs:
        return None
    # 避开纯新闻类，优先生活/娱乐/美食等
    prefer = [x for x in xs if any(k in x["title"] for k in
              ("吃", "笑", "猫", "狗", "雪", "冬天", "电影", "剧", "游戏", "歌", "舞", "旅行", "穿搭", "火锅"))]
    return random.choice(prefer or xs)
