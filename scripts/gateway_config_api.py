from pathlib import Path
import ast

# 1) life_core_client 加 options
p = Path(r"D:\大肥鱼\anshiyu-server\life_core_client.py")
s = p.read_text(encoding="utf-8")
if "def get_options" not in s:
    s = s.replace("    def set_mode(self, payload):",
"""    def get_options(self):
        return self._req("GET", "/options")

    def set_options(self, payload):
        return self._req("POST", "/options", payload)

    def set_mode(self, payload):""")
    p.write_text(s, encoding="utf-8")
    print("life_core_client 已加 options")
else:
    print("life_core_client 已存在")

# 2) 网关：memory config + persona config
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/memory/config" not in s:
    s = s.replace('STICKERS_JSON = BASE / "persona" / "stickers.json"',
'''STICKERS_JSON = BASE / "persona" / "stickers.json"
PERSONALITY_JSON = BASE / "persona" / "personality.json"


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
        "\\n\\n【她的性格】"
        f"她说话{parts[0]}，{parts[1]}，{parts[2]}，{freq_txt}。"
        "这些是她长期形成的倾向，要自然体现在语气里，不要直接说出来。"
    )''')

    s = s.replace('@app.get("/api/sticker/{meme_id}")',
'''@app.get("/api/memory/config")
async def get_memory_config(token: str = Query("")):
    auth(token)
    try:
        return {"ok": True, **(life_core.get_options() or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/memory/config")
async def set_memory_config(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    try:
        r = life_core.set_options(body)
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


@app.get("/api/sticker/{meme_id}")''')

    # chat 应用性格
    s = s.replace("""    try:
        system_prompt = ask_system_with_meme(system_prompt)
    except Exception:
        pass""",
"""    try:
        system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()
    except Exception:
        pass""")
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("网关记忆/性格接口已加")
else:
    print("已存在")