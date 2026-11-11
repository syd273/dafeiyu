from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "import trends" not in s:
    s = s.replace("try:\n    import music  # noqa: E402",
"""try:
    import trends  # noqa: E402
except Exception:
    trends = None
try:
    import music  # noqa: E402""")
    # chat 注入热点
    s = s.replace("""        legacy = _latest_legacy_summary()
        if legacy:""",
"""        if trends is not None:
            system_prompt += trends.prompt_block()
        legacy = _latest_legacy_summary()
        if legacy:""")
    # /api/trends
    s = s.replace('@app.get("/api/music/recommend")',
'''@app.get("/api/trends")
async def get_trends(token: str = Query("")):
    auth(token)
    if trends is None:
        return {"ok": False, "error": "trends unavailable"}
    return {"ok": True, **trends.all_trends()}


@app.get("/api/music/recommend")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("冲浪能力已接入")
else:
    print("已存在")