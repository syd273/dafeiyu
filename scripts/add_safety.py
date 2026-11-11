from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "import safety" not in s:
    s = s.replace("try:\n    import trends  # noqa: E402",
"""try:
    import safety  # noqa: E402
except Exception:
    safety = None
try:
    import trends  # noqa: E402""")

    # chat 入口：用户输入安全 + 回复过滤
    s = s.replace("""    # 表情包引导（追加到系统提示）""",
"""    # 内容安全：用户输入检查
    if safety is not None:
        hit = safety.check(text)
        if hit.get("hit"):
            return {"reply": safety.reject_message(hit.get("category", "")),
                    "mood": persona_core.current_mood().get("mood", "平静"),
                    "life": life_core.current(), "blocked": True}
    # 表情包引导（追加到系统提示）""")

    s = s.replace("""    reply = _decorate_meme(reply, mood)""",
"""    if safety is not None:
        reply, _hit = safety.filter_reply(reply)
    reply = _decorate_meme(reply, mood)""")

    # 说说生成也过滤
    s = s.replace("""    text = (text or "").strip()
    if not text:
        return ""
    life_core.add_feed(text, persona_core.current_mood().get("mood", "平静"), "talk")""",
"""    text = (text or "").strip()
    if not text:
        return ""
    if safety is not None:
        text, _hit = safety.filter_reply(text)
    life_core.add_feed(text, persona_core.current_mood().get("mood", "平静"), "talk")""")
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("内容安全已接入")
else:
    print("已存在")