# -*- coding: utf-8 -*-
"""B 站：让她能"刷"热门视频，并挑一个分享给阿东。"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import requests

BASE = Path(__file__).parent
CACHE = BASE / ".bili_cache.json"
CACHE_TTL = 1800  # 30 分钟

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}


def _fetch() -> list[dict]:
    urls = [
        "https://api.bilibili.com/x/web-interface/popular?ps=30&pn=1",
        "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all",
    ]
    s = requests.Session()
    s.trust_env = False
    for u in urls:
        try:
            r = s.get(u, headers=HEADERS, timeout=20)
            d = r.json()
            items = (d.get("data") or {}).get("list") or []
            out = []
            for it in items:
                bvid = it.get("bvid")
                title = (it.get("title") or "").strip()
                owner = ((it.get("owner") or {}).get("name") or "").strip()
                if bvid and title:
                    out.append({
                        "title": title,
                        "owner": owner,
                        "bvid": bvid,
                        "url": f"https://www.bilibili.com/video/{bvid}",
                        "desc": (it.get("desc") or "")[:120],
                    })
            if out:
                return out
        except Exception:
            continue
    return []


def videos(force: bool = False) -> list[dict]:
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


def random_video() -> dict | None:
    vs = videos()
    if not vs:
        return None
    return random.choice(vs)
