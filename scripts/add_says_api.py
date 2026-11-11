from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/says" not in s:
    s = s.replace('@app.get("/api/feed")',
'''@app.get("/api/says")
async def get_says(token: str = Query(""), limit: int = 50):
    """她的说说（feed 中 kind=talk）"""
    auth(token)
    try:
        items = [x for x in life_core.load_feed() if str(x.get("kind", "")) in ("talk", "")]
        return {"ok": True, "items": items[: max(1, min(limit, 100))]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/api/say")
async def post_say(token: str = Query("")):
    """让她现在发一条说说"""
    auth(token)
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            "\\n\\n你正在发一条说说（像朋友圈/空间动态），一句到两句，口语、有点生活气，"
            "可以带一点此刻的心情或刚发生的小事。只写说说正文，不要加引号或标题。"
        )
        text = ask_llm(system, [{"role": "user", "content": "（发一条说说）"}], max_tokens=160)
        text = (text or "").strip()
        if not text:
            return {"ok": False, "error": "生成失败"}
        life_core.add_feed(text, persona_core.current_mood().get("mood", "平静"), "talk")
        try:
            await broadcast({"type": "say", "text": text, "ts": int(time.time())})
        except Exception:
            pass
        return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/feed")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("说说接口已加")
else:
    print("已存在")