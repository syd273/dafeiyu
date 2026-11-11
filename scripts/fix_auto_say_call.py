from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''async def proactive_loop():
    cfg_path = BASE / "persona" / "proactive.json"
    while True:
        await asyncio.sleep(60)
        try:''',
'''async def proactive_loop():
    cfg_path = BASE / "persona" / "proactive.json"
    while True:
        await asyncio.sleep(60)
        try:
            await _maybe_auto_say()''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("调用已加")