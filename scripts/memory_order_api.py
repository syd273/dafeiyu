from pathlib import Path
import ast, json
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 1) 记录按星序返回
s = s.replace("""    stars = _load_stars()
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
    return {"ok": True, "total": len(rows), "items": rows[:limit]}""",
"""    stars = _load_stars()
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
    return {"ok": True, "total": len(rows), "items": rows[:limit]}""")

# 2) 删除后重排编号 + 同步 sync_state
s = s.replace("""    rest = [st for st in stars if st.get("id") != mid]
    if len(rest) == before:
        return {"ok": False, "error": "not found"}
    _save_stars(rest)
    return {"ok": True, "deleted": mid, "remaining": len(rest)}""",
"""    rest = [st for st in stars if st.get("id") != mid]
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
    return {"ok": True, "deleted": mid, "remaining": len(rest)}""")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("后端已更新")