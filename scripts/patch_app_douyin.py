from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 引入 douyin + 静态目录
s = s.replace("""try:
    import bili  # noqa: E402
except Exception:
    bili = None""",
"""try:
    import bili  # noqa: E402
except Exception:
    bili = None
try:
    import douyin  # noqa: E402
except Exception:
    douyin = None""")

s = s.replace('from fastapi import FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect',
              'from fastapi import FastAPI, Header, HTTPException, Query, Request, WebSocket, WebSocketDisconnect\nfrom fastapi.staticfiles import StaticFiles\nfrom fastapi.responses import FileResponse')

# 抖音分享接口 + 首页
s = s.replace('''@app.websocket("/ws")''',
'''@app.post("/api/share/douyin")
async def share_douyin(token: str = Query("")):
    auth(token)
    if douyin is None:
        raise HTTPException(status_code=500, detail="douyin not available")
    item = douyin.random_hot()
    if not item:
        raise HTTPException(status_code=502, detail="no hot item")
    system = persona_core.build_system_prompt(life=life_core.current())
    system += (f"\\n\\n你刚在抖音刷到一个热点：{item['title']}。"
               "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-3句，口语。")
    text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=160)
    text = text.rstrip() + "\\n" + item["url"]
    conn = kernel.connect()
    try:
        kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
    finally:
        conn.close()
    await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
    return {"text": text, "item": item}


@app.get("/")
async def index():
    return FileResponse(str(SERVER_DIR / "static" / "index.html"))


@app.websocket("/ws")''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("app patched")