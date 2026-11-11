from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/music/recommend" not in s:
    s = s.replace("import life_core  # noqa: E402",
"""import life_core  # noqa: E402
try:
    import music  # noqa: E402
except Exception:
    music = None""")

    s = s.replace('@app.get("/api/memory/config")',
'''@app.get("/api/music/recommend")
async def music_recommend(token: str = Query("")):
    """一起听歌：她选一首歌，并说一句推荐"""
    auth(token)
    if music is None:
        return {"ok": False, "error": "music module unavailable"}
    song = music.random_song()
    if not song:
        return {"ok": False, "error": "no songs"}
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            f"\\n\\n你刚挑了一首歌想和他一起听：《{song['title']}》（{song['owner']}）。"
            "说一句邀请/推荐，1-2 句，口语，不要提链接。"
        )
        text = ask_llm(system, [{"role": "user", "content": "（一起听歌）"}], max_tokens=160)
    except Exception:
        text = f"来，一起听这首《{song['title']}》吧。"
    return {"ok": True, "song": song, "text": text or f"一起听《{song['title']}》吧"}


@app.get("/api/music/talk")
async def music_talk(token: str = Query(""), title: str = Query(""), owner: str = Query("")):
    """听歌时她说一句感受"""
    auth(token)
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            f"\\n\\n你正和他一起听《{title}》（{owner}）。"
            "说一句听这首歌的感受或联想，1-2 句，口语，像陪在身边一起听。"
        )
        text = ask_llm(system, [{"role": "user", "content": "（听了一会儿）"}], max_tokens=180)
        return {"ok": True, "text": text or "这首歌还挺适合现在的。"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/memory/config")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("听歌接口已加")
else:
    print("已存在")