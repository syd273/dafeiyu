from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "life_bridge" not in s:
    s = s.replace("""try:
    import router  # noqa: E402
except Exception:
    router = None""",
"""try:
    import router  # noqa: E402
except Exception:
    router = None
try:
    import life_bridge  # noqa: E402
except Exception:
    life_bridge = None""")

    # 新路由：Life Core 状态 / 事件 / 上帝视角聚合
    s = s.replace('@app.get("/api/feed")', '''@app.get("/api/life/state")
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


@app.get("/api/godview")
async def godview(token: str = Query("")):
    """上帝视角聚合：生活状态 + 最近记忆 + 意图 + 事实"""
    auth(token)
    out = {"ok": True, "life_core": None, "recent": [], "intents": [], "facts": []}
    if life_bridge is not None:
        st = life_bridge.state()
        out["life_core"] = st
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


@app.get("/api/feed")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("routes added")
else:
    print("already")