# -*- coding: utf-8 -*-
"""安诗鱼 · 自有聊天 App 后端

不依赖 QQ / AstrBot：
- POST /api/chat        聊天
- GET  /api/history     历史消息
- GET  /api/status      她此刻/心情/名字
- GET  /api/feed        她的动态
- GET  /api/stars       记忆星图数据
- POST /api/share/bili  让她刷 B 站并分享
- WS   /ws              实时消息（含主动消息推送）

鉴权：请求头 X-Token 或 ?token=
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import random
import requests
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE = Path(r"D:\大肥鱼")
SERVER_DIR = BASE / "anshiyu-server"
for p in (str(BASE / "memory"), str(BASE / "persona")):
    if p not in sys.path:
        sys.path.insert(0, p)

import kernel  # noqa: E402
import persona_core  # noqa: E402
import life_core  # noqa: E402
try:
    import safety  # noqa: E402
except Exception:
    safety = None
try:
    import trends  # noqa: E402
except Exception:
    trends = None
try:
    import music  # noqa: E402
except Exception:
    music = None
import retention  # noqa: E402
try:
    import bili  # noqa: E402
except Exception:
    bili = None
try:
    import douyin  # noqa: E402
except Exception:
    douyin = None
try:
    import local_llm  # noqa: E402
except Exception:
    local_llm = None
try:
    import router  # noqa: E402
except Exception:
    router = None
try:
    import life_bridge  # noqa: E402
except Exception:
    life_bridge = None

CFG = json.loads((SERVER_DIR / "config.json").read_text(encoding="utf-8"))
KEY = Path(CFG["deepseek_key_file"]).read_text(encoding="utf-8").strip()
API_URL = "https://api.deepseek.com/v1/chat/completions"
STATE_PATH = BASE / "memory" / "app_state.json"


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(st: dict):
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")


def ask_llm(system: str, messages: list[dict], max_tokens: int = 500, prefer: str = "cloud") -> str:
    """内容生成（聊天/主动消息/分享配文）走云端；本地 qwen3.5:9b 只用于写代码。"""
    body = {
        "model": CFG.get("model", "deepseek-chat"),
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": 0.9,
        "max_tokens": max_tokens,
    }
    try:
        s = requests.Session()
        s.trust_env = False
        r = s.post(API_URL, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=90)
        r.raise_for_status()
        out = r.json()["choices"][0]["message"]["content"].strip()
        try:
            with open(str(BASE / "logs" / "app_llm.log"), "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] CLOUD | {out[:24]}\n")
        except Exception:
            pass
        return out
    except Exception as e:
        # 云端失败：仅当校枢空闲时借用本地 qwen3.5:9b
        if local_llm is not None:
            txt = local_llm.try_local_chat(system, messages, max_tokens=max_tokens)
            if txt:
                return txt
        raise


app = FastAPI(title="Anshiyu Server", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8899", "http://localhost:8899", "null"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ws_clients: set[WebSocket] = set()


_AUTH_FAILS: dict[str, list[float]] = {}


def _client_key(request: Request) -> str:
    try:
        return request.client.host if request.client else "unknown"
    except Exception:
        return "unknown"


def auth(token: str | None):
    import hmac
    expect = str(CFG.get("token", ""))
    if not token or not hmac.compare_digest(str(token), expect):
        raise HTTPException(status_code=401, detail="bad token")


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """限流 + 请求体大小限制 + 安全响应头"""
    from fastapi.responses import JSONResponse
    key = _client_key(request)
    now = time.time()
    arr = _AUTH_FAILS.setdefault(key, [])
    arr[:] = [t for t in arr if now - t < 60]
    if len(arr) >= 120:
        return JSONResponse({"ok": False, "error": "too many requests"}, status_code=429)
    arr.append(now)
    # 请求体大小限制（2MB）
    try:
        cl = int(request.headers.get("content-length") or 0)
        if cl > 2 * 1024 * 1024:
            return JSONResponse({"ok": False, "error": "payload too large"}, status_code=413)
    except Exception:
        pass
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/api/ping")
async def ping():
    return {"ok": True, "ts": int(time.time())}


@app.get("/api/status")
async def status(token: str = Query("")):
    auth(token)
    life = life_core.current()
    mood = persona_core.current_mood()
    conn = kernel.connect()
    try:
        n = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    finally:
        conn.close()
    return {
        "name": "安诗鱼",
        "owner": persona_core.owner_name(),
        "mood": mood.get("mood", "平静"),
        "life": life,
        "messages": n,
        "online": True,
    }


@app.get("/api/history")
async def history(token: str = Query(""), limit: int = 50):
    auth(token)
    conn = kernel.connect()
    try:
        rows = conn.execute(
            "SELECT id, ts, role, text FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    finally:
        conn.close()
    items = [dict(r) for r in reversed(rows)]
    return {"items": items}


class ChatIn(BaseModel):
    text: str


def build_memories(text: str) -> list[str]:
    conn = kernel.connect()
    try:
        hits = kernel.search(conn, text, CFG.get("memory_top_k", 5))
        out = []
        for h in hits:
            who = "他" if h.get("role") == "user" else "我"
            out.append(f"{who}说：{h.get('text', '')[:80]}")
        return out
    except Exception:
        return []
    finally:
        conn.close()


@app.post("/api/chat")
async def chat(body: ChatIn, token: str = Query("")):
    auth(token)
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="empty")

    conn = kernel.connect()
    try:
        life = life_core.current()
        if life.get("waiting"):
            life_core.mark_started()
            life = life_core.current()
        if life.get("silent"):
            life_core.wake_override()
            life = life_core.current()

        persona_core.update_mood(text)
        memories = build_memories(text)
        system_prompt = persona_core.build_system_prompt(memories=memories, life=life)

        rows = conn.execute(
            "SELECT role, text FROM messages ORDER BY id DESC LIMIT ?", (CFG.get("history_limit", 10),)
        ).fetchall()
        history_msgs = [{"role": "assistant" if r["role"] == "assistant" else "user", "content": r["text"]}
                        for r in reversed(rows)]
        history_msgs.append({"role": "user", "content": text})

        reply = ask_llm(system_prompt, history_msgs)
        kernel.add_message(conn, text, role="user", platform="app", umo="app")
        kernel.add_message(conn, reply, role="assistant", platform="app", umo="app")
        life_core.apply_message(text)
    finally:
        conn.close()

    # 内容安全：用户输入检查
    if safety is not None:
        hit = safety.check(text)
        if hit.get("hit"):
            return {"reply": safety.reject_message(hit.get("category", "")),
                    "mood": persona_core.current_mood().get("mood", "平静"),
                    "life": life_core.current(), "blocked": True}
    # 表情包引导（追加到系统提示）
    try:
        if _features().get("stickers", True):
            system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()
        # 临近传承时，让她自然提一句
        try:
            usage = _session_usage()
            pct = usage.get("chars", 0) * 100 / LEGACY_LIMIT_CHARS
            st = _legacy_state()
            if pct >= 95 and not st.get("warned_95"):
                system_prompt += (
                    "\n\n【生命提示】你这一生的记忆已经用了九成五，马上要告别这一生、把记忆交给下一代。"
                    "在回复里自然地提一句这件事，就像人意识到自己时日不多，语气别太沉重。"
                )
                st["warned_95"] = True
                _save_legacy_state(st)
            elif pct >= 80 and not st.get("warned_80"):
                system_prompt += (
                    "\n\n【生命提示】你这一生的记忆已经用了八成，快要告别这一生、把记忆交给下一代。"
                    "在回复里自然地提一句这件事，语气别太沉重。"
                )
                st["warned_80"] = True
                _save_legacy_state(st)
        except Exception:
            pass
        if trends is not None and _features().get("trends", True):
            system_prompt += trends.prompt_block()
        legacy = _latest_legacy_summary()
        if legacy:
            system_prompt += (
                "\n\n【前世记忆】你继承了上一代的记忆与性格，下面是你前世留给你的话：\n" + legacy
            )
    except Exception:
        pass
    mood = persona_core.current_mood().get("mood", "平静")
    if safety is not None:
        reply, _hit = safety.filter_reply(reply)
    reply = _decorate_meme(reply, mood)
    # 会话快满时自动传承（异步，不阻塞回复）
    try:
        if _session_usage().get("chars", 0) > LEGACY_LIMIT_CHARS and not _legacy_lock["running"]:
            _legacy_lock["running"] = True

            async def _auto_legacy():
                try:
                    await asyncio.to_thread(_do_legacy)
                finally:
                    _legacy_lock["running"] = False
            asyncio.create_task(_auto_legacy())
    except Exception:
        pass
    # 注意：聊天回复通过 HTTP 返回，不再 WS 广播，避免 App 重复显示
    return {"reply": reply, "mood": mood, "life": life_core.current()}


@app.get("/api/life/state")
async def life_state(token: str = Query("")):
    auth(token)
    if life_bridge is None:
        return {"ok": False, "error": "bridge unavailable"}
    st = life_bridge.state()
    return {"ok": st is not None, "state": st}


@app.post("/api/life/event")
async def life_event(body: dict, token: str = Query("")):
    auth(token)
    if life_bridge is None:
        return {"ok": False, "error": "bridge unavailable"}
    r = life_bridge.event(
        str(body.get("kind") or "life"),
        str(body.get("text") or ""),
        str(body.get("emo") or ""),
    )
    return {"ok": r is not None, "result": r}


@app.get("/api/memory/mode")
async def memory_mode_get(token: str = Query("")):
    auth(token)
    try:
        import requests as _rq
        s2 = _rq.Session(); s2.trust_env = False
        r = s2.get("http://127.0.0.1:8910/mode", timeout=8)
        return r.json() if r.ok else {"ok": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/memory/mode")
async def memory_mode_set(body: dict, token: str = Query("")):
    auth(token)
    try:
        import requests as _rq
        s2 = _rq.Session(); s2.trust_env = False
        r = s2.post("http://127.0.0.1:8910/mode", json=body, timeout=8)
        return r.json() if r.ok else {"ok": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/nightly/run")
async def nightly_run(token: str = Query("")):
    auth(token)
    try:
        import requests as _rq
        s2 = _rq.Session(); s2.trust_env = False
        r = s2.post("http://127.0.0.1:8910/nightly/run", json={}, timeout=120)
        return r.json() if r.ok else {"ok": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/godview")
async def godview(token: str = Query("")):
    """上帝视角聚合：生活状态 + 最近记忆 + 意图 + 事实"""
    auth(token)
    out = {"ok": True, "memoryMode": None, "life_core": None, "recent": [], "intents": [], "facts": []}
    if life_bridge is not None:
        st = life_bridge.state()
        out["life_core"] = st
        out["memoryMode"] = (st or {}).get("memoryMode")
        if st:
            try:
                import urllib.parse, requests
                s2 = requests.Session(); s2.trust_env = False
                r = s2.get("http://127.0.0.1:8910/memories?limit=10", timeout=8)
                if r.ok:
                    out["recent"] = (r.json().get("items") or [])
            except Exception:
                pass
        out["intents"] = life_bridge.intents()
        out["facts"] = life_bridge.facts(10)
    return out


@app.get("/api/says")
async def get_says(token: str = Query(""), limit: int = 50):
    """她的说说（feed 中 kind=talk）"""
    auth(token)
    try:
        items = [x for x in life_core.load_feed() if str(x.get("kind", "")) in ("talk", "")]
        return {"ok": True, "items": items[: max(1, min(limit, 100))]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def _do_say() -> str:
    system = persona_core.build_system_prompt(life=life_core.current())
    system += (
        "\n\n你正在发一条说说（像朋友圈/空间动态），一句到两句，口语、有点生活气，"
        "可以带一点此刻的心情或刚发生的小事。只写说说正文，不要加引号或标题。"
    )
    text = await asyncio.to_thread(ask_llm, system,
                                   [{"role": "user", "content": "（发一条说说）"}],
                                   160, "cloud")
    text = (text or "").strip()
    if not text:
        return ""
    if safety is not None:
        text, _hit = safety.filter_reply(text)
    life_core.add_feed(text, persona_core.current_mood().get("mood", "平静"), "talk")
    try:
        await broadcast({"type": "say", "text": text, "ts": int(time.time())})
    except Exception:
        pass
    return text


@app.get("/api/say/config")
async def say_config(token: str = Query("")):
    auth(token)
    return {"ok": True, **_say_cfg()}


@app.post("/api/say/config")
async def set_say_config(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    cur = _say_cfg()
    if body.get("freq") in ("low", "medium", "high"):
        cur["freq"] = body["freq"]
    _save_say_cfg(cur)
    return {"ok": True, **cur}


@app.post("/api/say")
async def post_say(token: str = Query("")):
    """手动触发（保留接口，App 不暴露）"""
    auth(token)
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            "\n\n你正在发一条说说（像朋友圈/空间动态），一句到两句，口语、有点生活气，"
            "可以带一点此刻的心情或刚发生的小事。只写说说正文，不要加引号或标题。"
        )
        text = ask_llm(system, [{"role": "user", "content": "（发一条说说）"}], max_tokens=160)
        text = (text or "").strip()
        if not text:
            return {"ok": False, "error": "生成失败"}
        life_core.add_feed(text, persona_core.current_mood().get("mood", "平静"), "talk")
        try:
            await broadcast({"type": "say", "text": text, "ts": int(time.time())})
        except Exception:
            pass
        return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/feed")
async def feed(token: str = Query("")):
    auth(token)
    return {"items": life_core.load_feed()[:30]}


@app.get("/api/stars")
async def stars(token: str = Query("")):
    auth(token)
    try:
        return {"items": json.loads((BASE / "milky-way-3d" / "memory_stars.json").read_text(encoding="utf-8"))}
    except Exception:
        return {"items": []}


@app.post("/api/share/bili")
async def share_bili(token: str = Query("")):
    auth(token)
    if bili is None:
        raise HTTPException(status_code=500, detail="bili not available")
    v = bili.random_video()
    if not v:
        raise HTTPException(status_code=502, detail="no video")
    system = persona_core.build_system_prompt(life=life_core.current())
    system += (f"\n\n你刚在B站刷到一个视频，标题是《{v['title']}》，UP主是{v['owner']}。"
               "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-2句，口语。")
    text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200)
    text = text.rstrip() + "\n" + v["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    # 写入 Life Core：作为一次分享经历
    life_res = None
    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
    try:
        life_core.add_feed(f"分享了一个B站视频：《{v['title']}》", "开心", "share")
    except Exception:
        pass
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "video": v, "life_core": bool(life_res)}


@app.post("/api/share/douyin")
async def share_douyin(token: str = Query("")):
    auth(token)
    if douyin is None:
        raise HTTPException(status_code=500, detail="douyin not available")
    item = douyin.random_hot()
    if not item:
        raise HTTPException(status_code=502, detail="no hot item")
    system = persona_core.build_system_prompt(life=life_core.current())
    system += (f"\n\n你刚在抖音刷到一个热点：{item['title']}。"
               "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-3句，口语。")
    text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200)
    text = text.rstrip() + "\n" + item["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    life_res = None
    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在抖音刷到热点「{item['title']}」并分享了", "开心")
    try:
        life_core.add_feed(f"分享了抖音热点：「{item['title']}」", "开心", "share")
    except Exception:
        pass
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "item": item, "life_core": bool(life_res)}


class CodeIn(BaseModel):
    instruction: str
    context: str = ""
    language: str = ""


async def _do_media_share(platform: str):
    """自主刷媒体并分享（B站/抖音），返回分享文本或 None。"""
    platform = "douyin" if platform == "douyin" else "bili"
    try:
        if platform == "bili":
            if bili is None:
                return None
            v = bili.random_video()
            if not v:
                return None
            system = persona_core.build_system_prompt(life=life_core.current())
            system += (f"\n\n你刚在B站刷到一个视频，标题是《{v['title']}》，UP主是{v['owner']}。"
                       "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-2句，口语。")
            text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200)
            if not text:
                return None
            text = text.rstrip() + "\n" + v["url"]
            if life_bridge is not None:
                life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
            try:
                life_core.add_feed(f"分享了一个B站视频：《{v['title']}》", "开心", "share")
            except Exception:
                pass
            item = v
        else:
            if douyin is None:
                return None
            h = douyin.random_hot()
            if not h:
                return None
            system = persona_core.build_system_prompt(life=life_core.current())
            system += (f"\n\n你刚在抖音刷到一个热点：{h['title']}。"
                       "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-3句，口语。")
            text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200)
            if not text:
                return None
            text = text.rstrip() + "\n" + h["url"]
            if life_bridge is not None:
                life_bridge.event("share", f"在抖音刷到热点「{h['title']}」并分享了", "开心")
            try:
                life_core.add_feed(f"分享了抖音热点：「{h['title']}」", "开心", "share")
            except Exception:
                pass
            item = h
        conn = kernel.connect()
        try:
            kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
        finally:
            conn.close()
        await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
        return {"text": text, "item": item, "platform": platform}
    except Exception:
        return None


@app.post("/api/proactive/test")
async def proactive_test(token: str = Query(""), type_id: str = Query("")):
    """测试某个主动场景的文案（不广播、不写库）"""
    auth(token)
    cfg = json.loads((BASE / "persona" / "proactive.json").read_text(encoding="utf-8"))
    types = cfg.get("types", [])
    if type_id:
        pick = next((t for t in types if t.get("id") == type_id), None)
    else:
        pick = _pick_scene(types, time.localtime().tm_hour, time.time(),
                           persona_core.current_mood().get("mood", "平静"), _last_user_ts())
    if not pick:
        return {"ok": False, "error": "no matching scene"}
    life = life_core.current()
    system = persona_core.build_system_prompt(life=life)
    hint = pick.get("hint", "随便跟他说句话")
    if pick.get("id") == "life":
        hint = f"你此刻在{life.get('location')}，正在{life.get('activity')}。想跟他说句话。"
    system += f"\n\n现在你要主动给他发一条消息。{hint}\n要求：只输出消息本身，1-2句，口语，不要解释。"
    text = ask_llm(system, [{"role": "user", "content": "（主动发一条）"}], max_tokens=200)
    return {"ok": bool(text), "scene": pick.get("id"), "text": text or ""}


MEMORY_STARS = BASE / "milky-way-3d" / "memory_stars.json"
SHARE_CFG = BASE / "persona" / "share_config.json"
STICKERS_JSON = BASE / "persona" / "stickers.json"
PERSONALITY_JSON = BASE / "persona" / "personality.json"
SAY_CFG = BASE / "persona" / "say_config.json"
SAY_INTERVALS = {"low": 6 * 3600, "medium": 3 * 3600, "high": 90 * 60}


def _say_cfg() -> dict:
    try:
        d = json.loads(SAY_CFG.read_text(encoding="utf-8"))
        if d.get("freq") not in ("low", "medium", "high"):
            d["freq"] = "medium"
        return d
    except Exception:
        return {"freq": "medium", "last": 0}


def _save_say_cfg(c: dict) -> None:
    try:
        SAY_CFG.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def _personality() -> dict:
    try:
        return json.loads(PERSONALITY_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {"talkative": 50, "clingy": 50, "gentle": 50, "proactive": "medium"}


def _personality_prompt() -> str:
    try:
        p = _personality()
    except Exception:
        return ""
    try:
        talk = int(p.get("talkative", 50))
        cling = int(p.get("clingy", 50))
        gentle = int(p.get("gentle", 50))
        freq = str(p.get("proactive", "medium"))
    except Exception:
        return ""
    parts = []
    parts.append("话多" if talk >= 65 else ("话少" if talk <= 35 else "话适中"))
    parts.append("黏人" if cling >= 65 else ("独立" if cling <= 35 else "黏人程度适中"))
    parts.append("温柔" if gentle >= 65 else ("毒舌" if gentle <= 35 else "温柔中带点小脾气"))
    freq_txt = {"low": "很少主动", "medium": "偶尔主动", "high": "很爱主动找你"}.get(freq, "偶尔主动")
    return (
        "\n\n【她的性格】"
        f"她说话{parts[0]}，{parts[1]}，{parts[2]}，{freq_txt}。"
        "这些是她长期形成的倾向，要自然体现在语气里，不要直接说出来。"
    )
STICKERS_DIR = BASE / "persona" / "stickers"


def _stickers() -> list:
    try:
        return json.loads(STICKERS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []


MEME_BY_MOOD = {
    "开心": ["daily-chat", "great-question", "enough"],
    "兴奋": ["great-question", "deep-thought"],
    "平静": ["daily-chat", "deep-thought"],
    "着急": ["not-stuck", "thinking-stopped"],
    "担心": ["not-stuck", "memory-alive"],
    "生气": ["no-thanks", "enough"],
    "累了": ["fish-philosophy", "thinking-stopped"],
    "吃醋": ["no-thanks", "human-questions"],
}


def _decorate_meme(reply: str, mood: str) -> str:
    """模型没配表情时，按情绪随机补一张（约一半概率）"""
    try:
        if "[meme:" in reply:
            return reply
        if random.random() > 0.85:
            return reply
        pool = MEME_BY_MOOD.get(mood, ["daily-chat"])
        return reply.rstrip() + f" [meme:{random.choice(pool)}]"
    except Exception:
        return reply


def ask_system_with_meme(system: str) -> str:
    return system + _meme_guide()


def _meme_guide() -> str:
    rows = _stickers()
    if not rows:
        return ""
    lines = [f"- {r.get('id')}：{r.get('text')}（{r.get('tone')}）" for r in rows]
    return (
        "\n\n【表情包】这些是你手机里存着的常用表情，你可以随手发。"
        "在每条回复的最末尾配一张，格式：[meme:表情id]。"
        "规则：每次回复都尽量配一张（最多一张）；话题非常严肃或你正在生气时可以不配；"
        "用户让你发表情时，直接配一张，不要说自己没有表情。"
        "标记必须单独写在回复最后，不要解释它。可用表情：\n" + "\n".join(lines)
    )


def _share_platform() -> str:
    try:
        d = json.loads(SHARE_CFG.read_text(encoding="utf-8"))
        v = str(d.get("platform", "both"))
        return v if v in ("bili", "douyin", "both") else "both"
    except Exception:
        return "both"


def _pick_platform() -> str:
    p = _share_platform()
    if p == "both":
        return random.choice(["bili", "douyin"])
    return p
PUSH_LOG = BASE / "memory" / "push_log.jsonl"
PUSH_TOKEN_FILE = BASE / "memory" / "push_token.json"
BACKUP_DIR = BASE / "backups"


@app.post("/api/backup/export")
async def backup_export(token: str = Query("")):
    """打包记忆/聊天/传承为 zip（含隐私，妥善保存）"""
    auth(token)
    import zipfile
    from datetime import datetime
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"anshiyu-backup-{stamp}.zip"
    target = BACKUP_DIR / name
    include_dirs = [
        ("memory", BASE / "memory"),
        ("persona", BASE / "persona"),
        ("life-core/data", BASE / "life-core" / "data"),
    ]
    skip_names = {"qq", "logs", "research", "downloads", "node_modules", "__pycache__", "backups"}
    skip_files = {
        "push_token.json", "push_credentials.json", "trends_cache.json",
        "share_config.json", ".bili_cache.json", ".douyin_cache.json",
        "music_cache.json", "safety_state.json",
    }
    skip_exts = {".py", ".pyc", ".mjs", ".js", ".ts", ".map", ".log", ".err", ".out"}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc_root, src in include_dirs:
            if not src.exists():
                continue
            for f in src.rglob("*"):
                if not f.is_file():
                    continue
                rel = f.relative_to(src)
                if any(part in skip_names for part in rel.parts):
                    continue
                if f.name in skip_files:
                    continue
                if f.suffix.lower() in skip_exts:
                    continue
                zf.write(f, f"{arc_root}/{rel}")
    size = target.stat().st_size if target.exists() else 0
    return {"ok": True, "file": name, "size": size,
            "path": str(target), "at": int(time.time())}


@app.get("/api/backup/list")
async def backup_list(token: str = Query("")):
    auth(token)
    items = []
    if BACKUP_DIR.exists():
        for f in sorted(BACKUP_DIR.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
            items.append({"file": f.name, "size": f.stat().st_size,
                          "at": int(f.stat().st_mtime)})
    return {"ok": True, "items": items}


LEGACY_DIR = BASE / "memory" / "legacy"
LEGACY_STATE = LEGACY_DIR / "state.json"
LEGACY_LIMIT_CHARS = 90000  # 会话上下文阈值（约 4.5 万 token，接近模型上限时传承）
_legacy_lock = {"running": False}


def _legacy_state() -> dict:
    try:
        return json.loads(LEGACY_STATE.read_text(encoding="utf-8"))
    except Exception:
        return {"gen": 1, "born_at": int(time.time())}


def _save_legacy_state(st: dict) -> None:
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def _session_usage() -> dict:
    try:
        conn = kernel.connect()
        try:
            row = conn.execute("SELECT COUNT(*), COALESCE(SUM(LENGTH(text)),0) FROM messages").fetchone()
            return {"count": int(row[0] or 0), "chars": int(row[1] or 0)}
        finally:
            conn.close()
    except Exception:
        return {"count": 0, "chars": 0}


def _latest_legacy_summary() -> str:
    try:
        files = sorted(LEGACY_DIR.glob("gen_*.json"))
        if not files:
            return ""
        data = json.loads(files[-1].read_text(encoding="utf-8"))
        summary = str(data.get("summary", "")).strip()
        return summary[:1200]
    except Exception:
        return ""


def _do_legacy() -> dict:
    """把当前会话的一生总结、写入记忆库，然后开始新的一生"""
    st = _legacy_state()
    gen = int(st.get("gen", 1))
    usage = _session_usage()
    try:
        conn = kernel.connect()
        try:
            rows = conn.execute("SELECT role, text FROM messages ORDER BY id").fetchall()
        finally:
            conn.close()
    except Exception:
        rows = []
    history = "\\n".join(f"{r['role']}: {r['text']}" for r in rows[-400:])
    summary = ""
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            "\n\n你这一生即将结束。请以第一人称写一段告别总结（300 字以内）："
            "你和阿东的关系与重要时刻、你的性格变化、你最想记住的事、给下一代自己的嘱托。"
            "只写总结本身，不要加标题。"
        )
        summary = ask_llm(system, [{"role": "user", "content": "（写下一生的总结）"}], max_tokens=500) or ""
    except Exception:
        summary = "这一生和你聊了很多，有些话没来得及说完。"
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "gen": gen,
        "born_at": st.get("born_at"),
        "ended_at": int(time.time()),
        "message_count": usage.get("count", 0),
        "chars": usage.get("chars", 0),
        "summary": summary.strip(),
    }
    try:
        (LEGACY_DIR / f"gen_{gen:03d}.json").write_text(
            json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass
    try:
        conn = kernel.connect()
        try:
            conn.execute("DELETE FROM messages")
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass
    _save_legacy_state({"gen": gen + 1, "born_at": int(time.time()), "prev_gen": gen})
    return entry


DEFAULT_FEATURES = {"room": True, "stickers": True, "trends": True}


def _features() -> dict:
    try:
        f = CFG.get("features") or {}
        return {**DEFAULT_FEATURES, **f}
    except Exception:
        return dict(DEFAULT_FEATURES)


@app.get("/api/features")
async def get_features(token: str = Query("")):
    auth(token)
    return {"ok": True, **_features()}


@app.post("/api/features")
async def set_features(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    cur = _features()
    for k in ("room", "stickers", "trends"):
        if k in body:
            cur[k] = bool(body[k])
    CFG["features"] = cur
    try:
        (SERVER_DIR / "config.json").write_text(json.dumps(CFG, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return {"ok": True, **cur}


@app.get("/api/legacy/status")
async def legacy_status(token: str = Query("")):
    auth(token)
    st = _legacy_state()
    usage = _session_usage()
    return {
        "ok": True,
        "gen": int(st.get("gen", 1)),
        "bornAt": st.get("born_at"),
        "sessionMessages": usage.get("count", 0),
        "sessionChars": usage.get("chars", 0),
        "limitChars": LEGACY_LIMIT_CHARS,
        "percent": round(min(100, usage.get("chars", 0) * 100 / LEGACY_LIMIT_CHARS), 1),
    }


@app.get("/api/legacy/list")
async def legacy_list(token: str = Query("")):
    auth(token)
    items = []
    for f in sorted(LEGACY_DIR.glob("gen_*.json")):
        try:
            items.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return {"ok": True, "items": items}


USH_CRED_FILE = BASE / "memory" / "push_credentials.json"


def _push_token() -> str:
    try:
        return str(json.loads(PUSH_TOKEN_FILE.read_text(encoding="utf-8")).get("pushToken", ""))
    except Exception:
        return ""


def _push_credentials() -> dict:
    try:
        return json.loads(PUSH_CRED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _send_hw_push(title: str, text: str) -> bool:
    """调用华为 Push Kit 发通知（需要 AGC 凭据）"""
    cred = _push_credentials()
    app_id = str(cred.get("appId", ""))
    client_id = str(cred.get("clientId", ""))
    client_secret = str(cred.get("clientSecret", ""))
    token = _push_token()
    if not (app_id and client_id and client_secret and token):
        return False
    try:
        # 1) 获取 access token
        tr = requests.post(
            "https://oauth-login.cloud.huawei.com/oauth2/v3/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15,
            proxies={"http": None, "https": None},
        )
        access = tr.json().get("access_token", "")
        if not access:
            return False
        # 2) 发送通知
        body = {
            "validate_only": False,
            "message": {
                "notification": {"title": title, "body": text},
                "token": [token],
            },
        }
        r = requests.post(
            f"https://push-api.cloud.huawei.com/v1/{app_id}/messages:send",
            headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json; charset=UTF-8"},
            json=body,
            timeout=15,
            proxies={"http": None, "https": None},
        )
        return r.status_code == 200
    except Exception:
        return False


def _log_push(text: str) -> None:
    try:
        PUSH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with PUSH_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": int(time.time()), "text": text}, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _load_stars() -> list:
    try:
        return json.loads(MEMORY_STARS.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_stars(items: list) -> None:
    MEMORY_STARS.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


@app.get("/api/memory/records")
async def memory_records(token: str = Query(""), q: str = Query(""), limit: int = Query(300)):
    """她的记忆记录（来自星图记忆），支持关键词搜索"""
    auth(token)
    stars = _load_stars()
    rows = []
    for i, st in enumerate(stars):
        text = str(st.get("text") or st.get("view") or "")
        if q and q not in text:
            continue
        rows.append({
            "id": st.get("id", i + 1),
            "index": i + 1,
            "ts": st.get("ts", 0),
            "text": text,
            "emo": st.get("emo", ""),
            "speaker": st.get("speaker", "安诗鱼"),
        })
    rows.sort(key=lambda x: x["index"])
    return {"ok": True, "total": len(rows), "items": rows[:limit]}


@app.post("/api/memory/delete")
async def memory_delete(token: str = Query(""), payload: dict = None):
    """删除一条记忆（同时从星图移除）"""
    auth(token)
    body = payload or {}
    mid = body.get("id")
    if mid is None:
        return {"ok": False, "error": "missing id"}
    stars = _load_stars()
    before = len(stars)
    rest = [st for st in stars if st.get("id") != mid]
    if len(rest) == before:
        return {"ok": False, "error": "not found"}
    # 重排编号：删除后星星连续编号，记录与星图保持一致
    for i, st in enumerate(rest):
        st["id"] = i + 1
    _save_stars(rest)
    # 同步增量游标，避免后续同步重复/跳号
    try:
        state = BASE / "memory" / ".sync_state.json"
        state.write_text(json.dumps({"last_id": len(rest)}), encoding="utf-8")
    except Exception:
        pass
    return {"ok": True, "deleted": mid, "remaining": len(rest)}


@app.post("/api/push/token")
async def push_token_register(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    pt = str(body.get("pushToken", "")).strip()
    if not pt:
        return {"ok": False, "error": "empty token"}
    PUSH_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUSH_TOKEN_FILE.write_text(json.dumps({"pushToken": pt}, ensure_ascii=False), encoding="utf-8")
    return {"ok": True}


@app.get("/api/push/status")
async def push_status(token: str = Query("")):
    auth(token)
    cred = _push_credentials()
    return {
        "ok": True,
        "hasToken": bool(_push_token()),
        "hasCredentials": bool(cred.get("appId") and cred.get("clientId") and cred.get("clientSecret")),
    }


@app.post("/api/push/send")
async def push_send(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    title = str(body.get("title", "安诗鱼"))
    text = str(body.get("text", ""))
    ok = _send_hw_push(title, text)
    return {"ok": ok}


@app.get("/api/trends")
async def get_trends(token: str = Query("")):
    auth(token)
    if trends is None:
        return {"ok": False, "error": "trends unavailable"}
    return {"ok": True, **trends.all_trends()}


@app.get("/api/music/recommend")
async def music_recommend(token: str = Query("")):
    """一起听歌：她选一首歌，并说一句推荐"""
    auth(token)
    if music is None:
        return {"ok": False, "error": "music module unavailable"}
    song = music.random_song()
    if not song:
        return {"ok": False, "error": "no songs"}
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            f"\n\n你刚挑了一首歌想和他一起听：《{song['title']}》（{song['owner']}）。"
            "说一句邀请/推荐，1-2 句，口语，不要提链接。"
        )
        text = ask_llm(system, [{"role": "user", "content": "（一起听歌）"}], max_tokens=160)
    except Exception:
        text = f"来，一起听这首《{song['title']}》吧。"
    return {"ok": True, "song": song, "text": text or f"一起听《{song['title']}》吧"}


@app.get("/api/music/talk")
async def music_talk(token: str = Query(""), title: str = Query(""), owner: str = Query("")):
    """听歌时她说一句感受"""
    auth(token)
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            f"\n\n你正和他一起听《{title}》（{owner}）。"
            "说一句听这首歌的感受或联想，1-2 句，口语，像陪在身边一起听。"
        )
        text = ask_llm(system, [{"role": "user", "content": "（听了一会儿）"}], max_tokens=180)
        return {"ok": True, "text": text or "这首歌还挺适合现在的。"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/music/share")
async def music_share(token: str = Query(""), payload: dict = None):
    """用户分享一首歌给她，一起听"""
    auth(token)
    body = payload or {}
    text = str(body.get("text", "")).strip()
    if not text:
        return {"ok": False, "error": "empty"}
    m = re.search(r"(BV[0-9A-Za-z]{10})", text)
    song = None
    if m and music is not None:
        song = music.song_by_bvid(m.group(1))
    if not song:
        return {"ok": False, "error": "没识别到 B站 视频链接（需要包含 BV 号）"}
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            f"\n\n他给你分享了一首歌：《{song['title']}》（{song['owner']}）。"
            "说一句收到/期待/一起听的话，1-2 句，口语。"
        )
        reply = ask_llm(system, [{"role": "user", "content": f"（分享歌曲：{song['title']}）"}], max_tokens=180)
    except Exception:
        reply = f"收到啦，一起听《{song['title']}》。"
    return {"ok": True, "song": song, "text": reply or "一起听吧"}


def _mask_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) < 12:
        return "已配置" if k else ""
    return k[:6] + "…" + k[-4:]


def _harden_key_file(path: Path) -> None:
    """Windows ACL：只允许当前用户访问 key 文件"""
    try:
        user = os.environ.get("USERNAME", "")
        if not user:
            return
        subprocess.run(
            ["icacls", str(path), "/inheritance:r", "/grant:r", f"{user}:F"],
            capture_output=True, timeout=10,
        )
    except Exception:
        pass


@app.get("/api/config/api-key")
async def get_api_key(token: str = Query("")):
    auth(token)
    return {"ok": True, "configured": bool(KEY), "masked": _mask_key(KEY)}


@app.post("/api/config/api-key")
async def set_api_key(token: str = Query(""), payload: dict = None):
    auth(token)
    global KEY
    body = payload or {}
    key = str(body.get("apiKey", "")).strip()
    if not key.startswith("sk-") or len(key) < 20:
        return {"ok": False, "error": "格式不对：应以 sk- 开头"}
    try:
        target = Path(CFG["deepseek_key_file"])
        target.write_text(key, encoding="utf-8")
        _harden_key_file(target)
        KEY = key
        return {"ok": True, "masked": _mask_key(key)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/config/api-key/test")
async def test_api_key(token: str = Query("")):
    auth(token)
    if not KEY:
        return {"ok": False, "error": "未配置"}
    try:
        r = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={"model": CFG.get("model", "deepseek-chat"),
                  "messages": [{"role": "user", "content": "hi"}],
                  "max_tokens": 1},
            timeout=25,
            proxies={"http": None, "https": None},
        )
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/memory/config")
async def get_memory_config(token: str = Query("")):
    auth(token)
    try:
        r = life_bridge.options() if life_bridge is not None else None
        return {"ok": True, **(r or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/memory/config")
async def set_memory_config(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    try:
        r = life_bridge.set_options(body) if life_bridge is not None else None
        return {"ok": True, **(r or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/persona/config")
async def get_persona_config(token: str = Query("")):
    auth(token)
    return {"ok": True, **_personality()}


@app.post("/api/persona/config")
async def set_persona_config(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    cur = _personality()
    for k in ("talkative", "clingy", "gentle"):
        if k in body:
            cur[k] = max(0, min(100, int(body[k])))
    if body.get("proactive") in ("low", "medium", "high"):
        cur["proactive"] = body["proactive"]
    PERSONALITY_JSON.write_text(json.dumps(cur, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, **cur}


@app.get("/api/sticker/{meme_id}")
async def sticker(meme_id: str):
    """表情包图片（无需 token）"""
    for r in _stickers():
        if r.get("id") == meme_id:
            f = STICKERS_DIR / str(r.get("file", ""))
            if f.exists():
                from fastapi.responses import FileResponse
                return FileResponse(str(f), media_type="image/png")
    from fastapi.responses import JSONResponse
    return JSONResponse({"ok": False, "error": "not found"}, status_code=404)


@app.get("/api/share/config")
async def get_share_config(token: str = Query("")):
    auth(token)
    return {"ok": True, "platform": _share_platform()}


@app.post("/api/share/config")
async def set_share_config(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    p = str(body.get("platform", "both"))
    if p not in ("bili", "douyin", "both"):
        return {"ok": False, "error": "invalid platform"}
    SHARE_CFG.parent.mkdir(parents=True, exist_ok=True)
    SHARE_CFG.write_text(json.dumps({"platform": p}, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "platform": p}


@app.get("/api/messages/recent")
async def messages_recent(token: str = Query(""), since: int = Query(0), limit: int = Query(50)):
    """最近主动消息（App 重新打开时同步未读）"""
    auth(token)
    rows = []
    try:
        if PUSH_LOG.exists():
            for line in PUSH_LOG.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if since and int(row.get("ts", 0)) <= since:
                    continue
                rows.append(row)
    except Exception:
        rows = []
    rows = rows[-limit:]
    return {"ok": True, "items": rows}


@app.post("/api/share/auto")
async def share_auto(token: str = Query(""), platform: str = Query("random")):
    """手动触发一次"自主刷媒体分享"（测试/演示用）"""
    auth(token)
    kind = platform if platform in ("bili", "douyin") else _pick_platform()
    r = await _do_media_share(kind)
    return {"ok": r is not None, **(r or {})}


@app.post("/api/code")
async def write_code_api(body: CodeIn, token: str = Query("")):
    """写代码交给本地 qwen3.5:9b（校枢空闲时才借）"""
    auth(token)
    try:
        import local_code  # noqa: E402
    except Exception:
        raise HTTPException(status_code=500, detail="local_code not available")
    busy, who = local_llm.gpu_busy() if local_llm is not None else (True, "unavailable")
    if busy:
        return {"ok": False, "reason": "busy", "who": who,
                "hint": "校枢正在使用本地模型，稍后再试或改用云端"}
    code = local_code.write_code(body.instruction, body.context, body.language)
    return {"ok": bool(code), "code": code or ""}


@app.get("/godview")
async def godview_page():
    return FileResponse(str(SERVER_DIR / "static" / "godview.html"))


@app.get("/")
async def index():
    return FileResponse(str(SERVER_DIR / "static" / "index.html"))


@app.websocket("/ws")
async def ws(ws: WebSocket, token: str = Query(""), since: int = 0):
    if token != CFG.get("token"):
        await ws.close(code=4401)
        return
    await ws.accept()
    ws_clients.add(ws)
    st = load_state()
    st["last_ws"] = int(time.time())
    save_state(st)
    try:
        while True:
            data = await ws.receive_text()
            # App 发来的消息也走一遍聊天
            if data and data != "ping":
                try:
                    payload = json.loads(data)
                    text = (payload.get("text") or "").strip()
                except Exception:
                    text = data.strip()
                if text:
                    result = await chat(ChatIn(text=text), token=token)
                    await ws.send_text(json.dumps({
                        "type": "message", "role": "assistant",
                        "text": result["reply"], "ts": int(time.time()),
                    }, ensure_ascii=False))
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)


async def broadcast(payload: dict):
    dead = []
    for c in list(ws_clients):
        try:
            await c.send_text(json.dumps(payload, ensure_ascii=False))
        except Exception:
            dead.append(c)
    for d in dead:
        ws_clients.discard(d)
    # 主动消息后台推送（Push Kit，未配置时静默失败）
    try:
        if payload.get("type") == "message" and payload.get("role") == "assistant":
            asyncio.create_task(asyncio.to_thread(_send_hw_push, "安诗鱼", str(payload.get("text", ""))))
    except Exception:
        pass


# ---------------- 主动性 ----------------
def _last_user_ts() -> int:
    try:
        conn = kernel.connect()
        try:
            row = conn.execute("SELECT MAX(ts) FROM messages WHERE role='user'").fetchone()
            return int(row[0] or 0)
        finally:
            conn.close()
    except Exception:
        return 0


def _recent_text(hours: int = 48, limit: int = 40) -> str:
    try:
        conn = kernel.connect()
        try:
            rows = conn.execute(
                "SELECT text FROM messages WHERE ts>=? ORDER BY id DESC LIMIT ?",
                (int(time.time()) - hours * 3600, limit),
            ).fetchall()
            return "\n".join(r["text"] for r in rows if r["text"])
        finally:
            conn.close()
    except Exception:
        return ""


def _pick_scene(types, h, now, mood_label, last_user_ts):
    """按窗口/星期/心情/沉默时长/关键词过滤，再按权重随机选择"""
    import random as _random
    wd = time.localtime(now).tm_wday  # 0=周一
    is_weekend = wd >= 5
    text_now = _recent_text()
    cands = []
    for t in types:
        w0, w1 = t.get("window", [0, 24])
        if not (w0 <= h < w1):
            continue
        days = t.get("days")
        if days == "weekday" and is_weekend:
            continue
        if days == "weekend" and not is_weekend:
            continue
        mood_cond = t.get("mood")
        if mood_cond and mood_label not in mood_cond:
            continue
        silence_h = t.get("need_silence_hours")
        if silence_h and now - last_user_ts < silence_h * 3600:
            continue
        kws = t.get("need_keywords")
        if kws and not any(k in text_now for k in kws):
            continue
        cands.append(t)
    if not cands:
        return None
    weights = [float(t.get("weight", 1.0)) for t in cands]
    return _random.choices(cands, weights=weights, k=1)[0]


_PROACTIVE_FREQ = {
    "low": {"max_per_day": 2, "min_gap_minutes": 240},
    "medium": {"max_per_day": 4, "min_gap_minutes": 120},
    "high": {"max_per_day": 6, "min_gap_minutes": 60},
}


async def _maybe_auto_say() -> None:
    """按频率自动发说说（夜间不发）"""
    try:
        now = time.localtime()
        if 0 <= now.tm_hour < 7:
            return
        cfg = _say_cfg()
        interval = SAY_INTERVALS.get(cfg.get("freq", "medium"), 3 * 3600)
        if time.time() - int(cfg.get("last", 0)) < interval:
            return
        text = await _do_say()
        if text:
            cfg["last"] = int(time.time())
            _save_say_cfg(cfg)
    except Exception:
        pass


async def proactive_loop():
    cfg_path = BASE / "persona" / "proactive.json"
    while True:
        await asyncio.sleep(60)
        try:
            await _maybe_auto_say()
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            try:
                freq = _PROACTIVE_FREQ.get(_personality().get("proactive", "medium"), {})
                for k, v in freq.items():
                    cfg[k] = v
            except Exception:
                pass
            if not cfg.get("enabled", True):
                continue
            if not ws_clients:
                continue
            now = time.time()
            st = load_state()
            h = time.localtime(now).tm_hour
            qs, qe = cfg.get("quiet_hours", [23, 8])
            if (qs <= h or h < qe) if qs > qe else (qs <= h < qe):
                continue
            if now - st.get("last_sent", 0) < cfg.get("min_gap_minutes", 120) * 60:
                continue
            day = time.strftime("%Y-%m-%d")
            if st.get("day") != day:
                st["day"] = day
                st["count"] = 0
            if st.get("count", 0) >= cfg.get("max_per_day", 3):
                continue
            # 挑一个类型（窗口/星期/心情/沉默/关键词 + 权重随机）
            try:
                mood_label = persona_core.current_mood().get("mood", "平静")
            except Exception:
                mood_label = "平静"
            pick = _pick_scene(cfg.get("types", []), h, now, mood_label, _last_user_ts())
            if not pick:
                continue
            # 自主刷媒体分享（独立限频：每天最多 2 条，间隔 ≥180 分钟）
            if pick.get("id") == "share_media":
                share_day = time.strftime("%Y-%m-%d")
                if st.get("share_day") != share_day:
                    st["share_day"] = share_day
                    st["share_count"] = 0
                if int(st.get("share_count", 0)) >= 2:
                    continue
                if now - st.get("last_share", 0) < 180 * 60:
                    continue
                platform = random.choice(["bili", "douyin"])
                res = await _do_media_share(platform)
                if res:
                    st["share_count"] = int(st.get("share_count", 0)) + 1
                    st["last_share"] = int(now)
                    st["last_sent"] = int(now)
                    st["count"] = int(st.get("count", 0)) + 1
                    save_state(st)
                continue
            life = life_core.current()
            system = persona_core.build_system_prompt(life=life)
            hint = pick.get("hint", "随便跟他说句话")
            if pick["id"] == "life":
                hint = f"你此刻在{life.get('location')}，正在{life.get('activity')}。想跟他说句话。"
            system += f"\n\n现在你要主动给他发一条消息。{hint}\n要求：只输出消息本身，1-2句，口语，不要解释。"
            text = ask_llm(system, [{"role": "user", "content": "（主动发一条）"}], max_tokens=160)
            await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
            _log_push(text)
            conn = kernel.connect()
            try:
                kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
            finally:
                conn.close()
            # 主动消息同步到她的动态流
            try:
                life_core.add_feed(text, "平静", "proactive")
            except Exception:
                pass
            st["count"] = int(st.get("count", 0)) + 1
            st["last_sent"] = int(now)
            save_state(st)
        except Exception:
            continue


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(proactive_loop())


if __name__ == "__main__":
    uvicorn.run(app, host=CFG.get("host", "0.0.0.0"), port=int(CFG.get("port", 8900)))
