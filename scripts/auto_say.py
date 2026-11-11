from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "SAY_CFG" not in s:
    s = s.replace('PERSONALITY_JSON = BASE / "persona" / "personality.json"',
'''PERSONALITY_JSON = BASE / "persona" / "personality.json"
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
        pass''')

    # 重构发说说函数（供手动与自动复用）
    s = s.replace('''@app.post("/api/say")
async def post_say(token: str = Query("")):
    """让她现在发一条说说"""
    auth(token)
    try:''',
'''async def _do_say() -> str:
    system = persona_core.build_system_prompt(life=life_core.current())
    system += (
        "\\n\\n你正在发一条说说（像朋友圈/空间动态），一句到两句，口语、有点生活气，"
        "可以带一点此刻的心情或刚发生的小事。只写说说正文，不要加引号或标题。"
    )
    text = await asyncio.to_thread(ask_llm, system,
                                   [{"role": "user", "content": "（发一条说说）"}],
                                   160, "cloud")
    text = (text or "").strip()
    if not text:
        return ""
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
    try:''')

    # 自动说说：在 proactive_loop 中检查
    s = s.replace('''async def proactive_loop():''',
'''async def _maybe_auto_say() -> None:
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


async def proactive_loop():''')

    # 在 proactive 主循环里调用（找到循环体）
    s = s.replace('''            await asyncio.sleep(60)''',
'''            await _maybe_auto_say()
            await asyncio.sleep(60)''', 1)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("自主说说已加")
else:
    print("已存在")