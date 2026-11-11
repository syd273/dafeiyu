# -*- coding: utf-8 -*-
"""一起听歌：B站音乐区排行（随机取歌）"""
import json
import random
import time
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
CACHE = BASE / "music_cache.json"
CACHE_TTL = 600
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}


def _fetch() -> list[dict]:
    urls = [
        "https://api.bilibili.com/x/web-interface/ranking/v2?rid=3&type=all",
    ]
    for u in urls:
        try:
            s = requests.Session()
            s.trust_env = False
            # 先访问首页拿 buvid cookie，否则排行接口会风控（-352）
            try:
                s.get("https://www.bilibili.com/", headers=HEADERS, timeout=15)
            except Exception:
                pass
            r = s.get(u, headers=HEADERS, timeout=20)
            data = r.json().get("data") or {}
            out = []
            for it in (data.get("list") or []):
                bvid = it.get("bvid")
                title = (it.get("title") or "").strip()
                owner = ((it.get("owner") or {}).get("name") or "").strip()
                pic = (it.get("pic") or "").strip()
                if pic.startswith("//"):
                    pic = "https:" + pic
                elif pic.startswith("http://"):
                    pic = pic.replace("http://", "https://", 1)
                if bvid and title:
                    out.append({
                        "title": title,
                        "owner": owner,
                        "bvid": bvid,
                        "url": f"https://www.bilibili.com/video/{bvid}",
                        "pic": pic,
                    })
            if out:
                return out
        except Exception:
            continue
    return []


def songs(force: bool = False) -> list[dict]:
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


def song_by_bvid(bvid: str) -> dict | None:
    """按 BV 号取视频信息（用户分享用）"""
    if not bvid:
        return None
    try:
        s = requests.Session()
        s.trust_env = False
        try:
            s.get("https://www.bilibili.com/", headers=HEADERS, timeout=15)
        except Exception:
            pass
        r = s.get(
            f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
            headers=HEADERS, timeout=20,
        )
        d = r.json()
        if d.get("code") != 0:
            return None
        v = d.get("data") or {}
        pic = (v.get("pic") or "").strip()
        if pic.startswith("http://"):
            pic = pic.replace("http://", "https://", 1)
        return {
            "title": (v.get("title") or "").strip(),
            "owner": ((v.get("owner") or {}).get("name") or "").strip(),
            "bvid": bvid,
            "url": f"https://www.bilibili.com/video/{bvid}",
            "pic": pic,
        }
    except Exception:
        return None


def random_song() -> dict | None:
    vs = songs()
    if not vs:
        return None
    return random.choice(vs)
