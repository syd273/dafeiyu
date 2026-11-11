from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

old = '''            await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
            conn = kernel.connect()
            try:
                kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
            finally:
                conn.close()
            st["count"] = int(st.get("count", 0)) + 1
            st["last_sent"] = int(now)
            save_state(st)'''
new = '''            await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
            conn = kernel.connect()
            try:
                kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
            finally:
                conn.close()
            # 主动消息同步到她的动态流
            try:
                life_core.add_feed(text, "平静")
            except Exception:
                pass
            st["count"] = int(st.get("count", 0)) + 1
            st["last_sent"] = int(now)
            save_state(st)'''
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("proactive feed sync added")
else:
    print("MISS")