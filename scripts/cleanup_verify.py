# -*- coding: utf-8 -*-
"""清理本次主动消息验证写入的测试数据（消息 + 记忆星）"""
import json
import sqlite3
import time
from pathlib import Path

B = Path(r"D:\大肥鱼")
conn = sqlite3.connect(B / "memory" / "archive.db")
cut = int(time.time()) - 3600
rows = conn.execute(
    "SELECT id, ts, role, substr(text,1,24) FROM messages WHERE ts >= ? ORDER BY id", (cut,)
).fetchall()
print("测试时段消息：")
for r in rows:
    print("  ", r)
ids = [r[0] for r in rows if r[2] == "assistant"]
if ids:
    conn.executemany("DELETE FROM messages WHERE id=?", [(i,) for i in ids])
    for t in ("emotion", "message_entities"):
        try:
            conn.executemany(f"DELETE FROM {t} WHERE msg_id=?", [(i,) for i in ids])
        except Exception:
            pass
    conn.commit()
    print("已删除测试消息:", len(ids))
conn.close()

stars_p = B / "milky-way-3d" / "memory_stars.json"
stars = json.loads(stars_p.read_text(encoding="utf-8"))
kept = [x for x in stars if int(x.get("ts", 0)) < cut]
if len(kept) != len(stars):
    stars_p.write_text(json.dumps(kept, ensure_ascii=False), encoding="utf-8")
    print("已删除记忆星:", len(stars) - len(kept))
else:
    print("无新增记忆星")

conn = sqlite3.connect(B / "memory" / "archive.db")
print("剩余 messages:", conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0])
conn.close()
print("剩余 stars:", len(json.loads(stars_p.read_text(encoding="utf-8"))))
