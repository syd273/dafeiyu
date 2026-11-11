from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/sticker" not in s:
    s = s.replace('SHARE_CFG = BASE / "persona" / "share_config.json"',
'''SHARE_CFG = BASE / "persona" / "share_config.json"
STICKERS_JSON = BASE / "persona" / "stickers.json"
STICKERS_DIR = BASE / "persona" / "stickers"


def _stickers() -> list:
    try:
        return json.loads(STICKERS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []


def _meme_guide() -> str:
    rows = _stickers()
    if not rows:
        return ""
    lines = [f"- {r.get('id')}：{r.get('text')}（{r.get('tone')}）" for r in rows]
    return (
        "\\n\\n【表情包】你可以在回复的最末尾加一个表情标记，格式：[meme:表情id]。"
        "规则：一次回复最多一个；只在轻松、开心、调侃、安慰时用；严肃话题不用；"
        "标记必须单独写在回复最后，不要解释它。可用表情：\\n" + "\\n".join(lines)
    )''')

    s = s.replace('@app.get("/api/share/config")',
'''@app.get("/api/sticker/{meme_id}")
async def sticker(meme_id: str):
    """表情包图片（无需 token）"""
    for r in _stickers():
        if r.get("id") == meme_id:
            f = STICKERS_DIR / str(r.get("file", ""))
            if f.exists():
                from fastapi.responses import FileResponse
                return FileResponse(str(f), media_type="image/png")
    from fastapi.responses import JSONResponse
    return JSONResponse({"ok": False, "error": "not found"}, status_code=404)


@app.get("/api/share/config")''')

    # chat 提示词追加表情引导
    s = s.replace('    mood = persona_core.current_mood().get("mood", "平静")',
'''    # 表情包引导（追加到系统提示）
    try:
        system = ask_system_with_meme(system)
    except Exception:
        pass
    mood = persona_core.current_mood().get("mood", "平静")''')

    s = s.replace('''def _meme_guide() -> str:''',
'''def ask_system_with_meme(system: str) -> str:
    return system + _meme_guide()


def _meme_guide() -> str:''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("表情路由与提示词已加")
else:
    print("已存在")