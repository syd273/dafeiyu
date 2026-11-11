from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/legacy/status" not in s:
    s = s.replace('PUSH_TOKEN_FILE = BASE / "memory" / "push_token.json"',
'''PUSH_TOKEN_FILE = BASE / "memory" / "push_token.json"
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
    history = "\n".join(f"{r['role']}: {r['text']}" for r in rows[-400:])
    summary = ""
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            "\\n\\n你这一生即将结束。请以第一人称写一段告别总结（300 字以内）："
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


@app.post("/api/legacy/trigger")
async def legacy_trigger(token: str = Query("")):
    auth(token)
    if _legacy_lock["running"]:
        return {"ok": False, "error": "正在传承中"}
    _legacy_lock["running"] = True
    try:
        entry = await asyncio.to_thread(_do_legacy)
        return {"ok": True, **entry}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        _legacy_lock["running"] = False''')

    # system prompt 注入前世记忆
    s = s.replace("""    try:
        system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()
    except Exception:
        pass""",
"""    try:
        system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()
        legacy = _latest_legacy_summary()
        if legacy:
            system_prompt += (
                "\\n\\n【前世记忆】你继承了上一代的记忆与性格，下面是你前世留给你的话：\\n" + legacy
            )
    except Exception:
        pass""")

    # chat 后自动检查传承
    s = s.replace("""    reply = _decorate_meme(reply, mood)
    # 注意：聊天回复通过 HTTP 返回，不再 WS 广播，避免 App 重复显示""",
"""    reply = _decorate_meme(reply, mood)
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
    # 注意：聊天回复通过 HTTP 返回，不再 WS 广播，避免 App 重复显示""")
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("传承机制已加")
else:
    print("已存在")