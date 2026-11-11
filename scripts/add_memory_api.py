from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/memory/records" not in s:
    s = s.replace('@app.post("/api/share/auto")', '''MEMORY_STARS = BASE / "milky-way-3d" / "memory_stars.json"


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
            "id": st.get("id", i),
            "index": i + 1,
            "ts": st.get("ts", 0),
            "text": text,
            "emo": st.get("emo", ""),
            "speaker": st.get("speaker", "安诗鱼"),
        })
    rows.sort(key=lambda x: x["ts"], reverse=True)
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
    _save_stars(rest)
    return {"ok": True, "deleted": mid, "remaining": len(rest)}


@app.post("/api/share/auto")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("记忆接口已加")
else:
    print("已存在")