import sqlite3, json
from pathlib import Path
DB = r"D:\大肥鱼\memory\archive.db"
c = sqlite3.connect(DB)
for t in ("message_entities","emotion","edges","summaries","facts","entities","messages"):
    try: c.execute(f"DELETE FROM {t}")
    except Exception as e: print("skip", t, e)
try: c.execute("DELETE FROM sqlite_sequence")
except Exception: pass
c.commit()
counts = {t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("messages","emotion","entities","edges","message_entities","summaries","facts")}
c.close()
print("清空后:", counts)
Path(r"D:\大肥鱼\milky-way-3d\memory_stars.json").write_text("[]", encoding="utf-8")
Path(r"D:\大肥鱼\memory\.sync_state.json").write_text(json.dumps({"last_id": 0}), encoding="utf-8")
print("星图 JSON 已重置")