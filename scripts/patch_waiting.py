from pathlib import Path
import ast

# 1) life_core：未开始对话前返回 waiting
p = Path(r"D:\大肥鱼\persona\life_core.py")
s = p.read_text(encoding="utf-8")
if "def mark_started" not in s:
    s = s.replace("def current() -> dict:", '''def mark_started():
    st = load_state()
    if not st.get("started"):
        st["started"] = True
        save_state(st)


def current() -> dict:
    st0 = load_state()
    if not st0.get("started"):
        return {"waiting": True, "ts": int(time.time()), "location": "", "activity": "",
                "event": "", "silent": True, "period": "", "date": time.strftime("%Y-%m-%d")}''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("life_core waiting ok")

# 2) sync：有消息后标记开始
p = Path(r"D:\大肥鱼\scripts\sync_memories.py")
s = p.read_text(encoding="utf-8")
if "mark_started" not in s:
    s = s.replace("    for name in (\"life_state.json\", \"feed.json\"):", '''    try:
        import sqlite3 as _sq
        _c = _sq.connect(BASE / "memory" / "archive.db")
        _n = _c.execute("SELECT COUNT(*) FROM messages WHERE role='user'").fetchone()[0]
        _c.close()
        if _n > 0 and life_core is not None:
            life_core.mark_started()
    except Exception:
        pass
    for name in ("life_state.json", "feed.json"):''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("sync mark_started ok")