import json, sqlite3, re
from pathlib import Path
db = r"D:\大肥鱼\memory\archive.db"
out = Path(r"D:\大肥鱼\milky-way-3d\memory_stars.json")
c = sqlite3.connect(db); c.row_factory = sqlite3.Row
rows = c.execute("""SELECT m.id, m.ts, m.role, m.text, COALESCE(e.label,'平静') emo
  FROM messages m LEFT JOIN emotion e ON e.msg_id=m.id ORDER BY m.ts ASC""").fetchall()
c.close()
def her_view(t):
    t = (t or "").strip()
    t = t.replace("大肥鱼", "安诗鱼")
    t = t.replace("我们", "他们").replace("我的", "他的").replace("我自己", "他自己")
    return re.sub(r"我(?![们])", "他", t)
data = []
for r in rows:
    raw = (r["text"] or "").strip()
    if not raw: continue
    role = r["role"]
    if role == "assistant":
        view = raw.replace("大肥鱼", "安诗鱼")
        speaker = "安诗鱼"
    else:
        view = her_view(raw); speaker = "他"
    data.append({"id": r["id"], "ts": r["ts"], "role": role, "emo": r["emo"],
                 "text": raw, "view": view, "speaker": speaker})
out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
print("exported", len(data), "| 样例:", data[-1]["view"][:50])