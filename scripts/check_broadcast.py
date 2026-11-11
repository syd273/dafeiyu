from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "_send_hw_push" in s and "create_task(asyncio.to_thread(_send_hw_push" not in s:
    # 找到 broadcast 定义
    import re as _re
    m = _re.search(r"async def broadcast\(([^)]*)\):", s)
    print("broadcast 定义:", m.group(0) if m else "未找到")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("检查完成")