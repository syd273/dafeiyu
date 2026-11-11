import json, sqlite3, time
from pathlib import Path
BASE = Path(r"D:\大肥鱼")
DB = BASE / "memory" / "archive.db"

# 1) 记忆库清空
c = sqlite3.connect(DB)
for t in ("message_entities", "emotion", "edges", "summaries", "facts", "entities", "messages"):
    try:
        c.execute(f"DELETE FROM {t}")
    except Exception as e:
        print("skip", t, e)
try:
    c.execute("DELETE FROM sqlite_sequence")
except Exception:
    pass
c.commit()
counts = {t: c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
          for t in ("messages","emotion","entities","edges","message_entities","summaries","facts")}
c.close()

# 2) 星图与同步状态
(BASE / "milky-way-3d" / "memory_stars.json").write_text("[]", encoding="utf-8")
(BASE / "memory" / ".sync_state.json").write_text(json.dumps({"last_id": 0}), encoding="utf-8")

# 3) 保持度 / 说说 / 生活状态 / 主动状态 / 心情
(BASE / "persona" / "retention.json").write_text("{}", encoding="utf-8")
(BASE / "persona" / "feed.json").write_text("[]", encoding="utf-8")
(BASE / "persona" / "life_state.json").write_text("{}", encoding="utf-8")
(BASE / "memory" / "proactive_state.json").write_text(json.dumps({"count": 0, "day": "", "fired": {}, "sent_texts": [], "last_sent": 0}, ensure_ascii=False), encoding="utf-8")
(BASE / "persona" / "mood.json").write_text(json.dumps({"mood": "平静", "score": 0.5, "ts": int(time.time()), "turns": 0}, ensure_ascii=False), encoding="utf-8")

print("记忆库:", counts)
print("星图/保持度/说说/生活/主动/心情 已清零")