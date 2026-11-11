from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

old_bili = '''    text = text.rstrip() + "\\n" + v["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "video": v}'''
new_bili = '''    text = text.rstrip() + "\\n" + v["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    # 写入 Life Core：作为一次分享经历
    life_res = None
    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "video": v, "life_core": bool(life_res)}'''

old_dy = '''    text = text.rstrip() + "\\n" + item["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "item": item}'''
new_dy = '''    text = text.rstrip() + "\\n" + item["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    life_res = None
    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在抖音刷到热点「{item['title']}」并分享了", "开心")
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "item": item, "life_core": bool(life_res)}'''

if old_bili in s and old_dy in s:
    s = s.replace(old_bili, new_bili).replace(old_dy, new_dy)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("share routes patched")
else:
    print("MISS", old_bili in s, old_dy in s)