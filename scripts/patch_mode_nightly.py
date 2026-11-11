from pathlib import Path
import ast

# 1) 修复 state 的 cached 判断（调用 episodes() 以在 full 模式重建缓存）
p = Path(r"D:\大肥鱼\life-core\src\server.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("""    const opts = options();
    return {
      ok: true,
      service: 'anshiyu-life-core',
      version: 4,
      memoryMode: opts.memoryMode,
      cached: episodeCache ? episodeCache.length : 0,""",
"""    const opts = options();
    const eps = episodes(); // full 模式下确保缓存已建立
    return {
      ok: true,
      service: 'anshiyu-life-core',
      version: 4,
      memoryMode: opts.memoryMode,
      cached: opts.memoryMode === 'full' ? eps.length : 0,""")
p.write_text(s, encoding="utf-8")
print("state cache fixed")

# 2) 网关新增模式与夜间代理
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "/api/memory/mode" not in s:
    s = s.replace('@app.get("/api/godview")', '''@app.get("/api/memory/mode")
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


@app.get("/api/godview")''')
    # godview 附带 memoryMode
    s = s.replace('    out = {"ok": True, "life_core": None, "recent": [], "intents": [], "facts": []}',
                  '    out = {"ok": True, "memoryMode": None, "life_core": None, "recent": [], "intents": [], "facts": []}')
    s = s.replace('        out["life_core"] = st',
                  '        out["life_core"] = st\n        out["memoryMode"] = (st or {}).get("memoryMode")')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("gateway routes added")
else:
    print("already")