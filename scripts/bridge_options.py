from pathlib import Path
import ast

# 1) life_bridge 加 options
p = Path(r"D:\大肥鱼\anshiyu-server\life_bridge.py")
s = p.read_text(encoding="utf-8")
if "def options(" not in s:
    s = s.replace("def available() -> bool:",
'''def options() -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.get_options()
        return r if r.get("ok") else None
    except Exception:
        return None


def set_options(payload: dict) -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.set_options(payload or {})
        return r if r.get("ok") else None
    except Exception:
        return None


def available() -> bool:''')
    p.write_text(s, encoding="utf-8")
    print("life_bridge 已加 options")

# 2) 网关改用 life_bridge
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    try:
        return {"ok": True, **(life_core.get_options() or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}''',
'''    try:
        r = life_bridge.options() if life_bridge is not None else None
        return {"ok": True, **(r or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}''')
s = s.replace('''    try:
        r = life_core.set_options(body)
        return {"ok": True, **(r or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}''',
'''    try:
        r = life_bridge.set_options(body) if life_bridge is not None else None
        return {"ok": True, **(r or {})}
    except Exception as e:
        return {"ok": False, "error": str(e)}''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("网关已改用 life_bridge")