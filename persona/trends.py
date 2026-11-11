# -*- coding: utf-8 -*-
"""网上冲浪：抓 B站 热搜 + 微博热搜，给她"网感"和近期梗"""
import json
import time
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
CACHE = BASE / "trends_cache.json"
TTL = 1800  # 30 分钟刷新
BILI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}
WEIBO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://weibo.com/",
    "Accept": "application/json, text/plain, */*",
}


def fetch_bili() -> list[dict]:
    try:
        s = requests.Session()
        s.trust_env = False
        try:
            s.get("https://www.bilibili.com/", headers=BILI_HEADERS, timeout=15)
        except Exception:
            pass
        r = s.get(
            "https://api.bilibili.com/x/web-interface/search/square?limit=15",
            headers=BILI_HEADERS, timeout=20,
        )
        d = r.json()
        if d.get("code") != 0:
            return []
        out = []
        for x in (d.get("data", {}).get("trending", {}).get("list") or []):
            kw = (x.get("keyword") or "").strip()
            if kw:
                out.append({"source": "bili", "title": kw, "hot": x.get("heat_score") or 0})
        return out
    except Exception:
        return []


def fetch_weibo() -> list[dict]:
    try:
        s = requests.Session()
        s.trust_env = False
        r = s.get("https://weibo.com/ajax/side/hotSearch", headers=WEIBO_HEADERS, timeout=20)
        d = r.json()
        if not d.get("ok"):
            return []
        out = []
        for x in (d.get("data", {}).get("realtime") or [])[:15]:
            w = (x.get("word") or "").strip()
            if w:
                out.append({"source": "weibo", "title": w, "hot": x.get("num") or 0})
        return out
    except Exception:
        return []


def all_trends(force: bool = False) -> dict:
    if not force and CACHE.exists() and time.time() - CACHE.stat().st_mtime < TTL:
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    items = fetch_bili() + fetch_weibo()
    data = {"updated": int(time.time()), "items": items}
    if items:
        try:
            CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    return data


def prompt_block(limit: int = 8) -> str:
    """给聊天提示词用的热点/梗块"""
    d = all_trends()
    titles = [x["title"] for x in d.get("items", [])[:limit] if x.get("title")]
    if not titles:
        return ""
    return (
        "\n\n【最近网上在聊】\n"
        + "\n".join(f"- {t}" for t in titles)
        + "\n你知道这些近期热点和网络梗，聊天时可以自然接梗、接话，但不要强行提起。"
    )
