from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if 'godview.html' not in s:
    s = s.replace('@app.get("/")', '''@app.get("/godview")
async def godview_page():
    return FileResponse(str(SERVER_DIR / "static" / "godview.html"))


@app.get("/")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("godview route added")
else:
    print("already")