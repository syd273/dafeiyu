from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 1) 主动消息日志文件
s = s.replace('MEMORY_STARS = BASE / "milky-way-3d" / "memory_stars.json"',
'''MEMORY_STARS = BASE / "milky-way-3d" / "memory_stars.json"
PUSH_LOG = BASE / "memory" / "push_log.jsonl"


def _log_push(text: str) -> None:
    try:
        PUSH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with PUSH_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": int(time.time()), "text": text}, ensure_ascii=False) + "\\n")
    except Exception:
        pass''')

# 2) 最近主动消息接口
if "/api/messages/recent" not in s:
    s = s.replace('@app.post("/api/share/auto")',
'''@app.get("/api/messages/recent")
async def messages_recent(token: str = Query(""), since: int = Query(0), limit: int = Query(50)):
    """最近主动消息（App 重新打开时同步未读）"""
    auth(token)
    rows = []
    try:
        if PUSH_LOG.exists():
            for line in PUSH_LOG.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if since and int(row.get("ts", 0)) <= since:
                    continue
                rows.append(row)
    except Exception:
        rows = []
    rows = rows[-limit:]
    return {"ok": True, "items": rows}


@app.post("/api/share/auto")''')
    # 在 broadcast 时记录（proactive/share 都记录）
    s = s.replace('''            await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})''',
'''            await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
            _log_push(text)''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("离线同步接口已加")