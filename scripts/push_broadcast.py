from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace("""    for d in dead:
        ws_clients.discard(d)


# ---------------- 主动性 ----------------""",
"""    for d in dead:
        ws_clients.discard(d)
    # 主动消息后台推送（Push Kit，未配置时静默失败）
    try:
        if payload.get("type") == "message" and payload.get("role") == "assistant":
            asyncio.create_task(asyncio.to_thread(_send_hw_push, "安诗鱼", str(payload.get("text", ""))))
    except Exception:
        pass


# ---------------- 主动性 ----------------""")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("推送已接入广播")