from pathlib import Path
import json
p = Path(r"D:\大肥鱼\scripts\sync_memories.py")
s = p.read_text(encoding="utf-8")
if "schedule.json" not in s:
    s = s.replace('    for name in ("life_state.json", "feed.json"):', '''    try:
        import json as _json
        life = _json.loads((src_dir / "life.json").read_text(encoding="utf-8"))
        (dst_dir / "schedule.json").write_text(_json.dumps(
            {"schedule": life.get("schedule", [])}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    for name in ("life_state.json", "feed.json"):''')
    p.write_text(s, encoding="utf-8")
    print("sync schedule ok")