from pathlib import Path
import ast, re

# 1) music.py 加 song_by_bvid
p = Path(r"D:\大肥鱼\persona\music.py")
s = p.read_text(encoding="utf-8")
if "def song_by_bvid" not in s:
    s = s.replace("def random_song() -> dict | None:",
'''def song_by_bvid(bvid: str) -> dict | None:
    """按 BV 号取视频信息（用户分享用）"""
    if not bvid:
        return None
    try:
        s = requests.Session()
        s.trust_env = False
        try:
            s.get("https://www.bilibili.com/", headers=HEADERS, timeout=15)
        except Exception:
            pass
        r = s.get(
            f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
            headers=HEADERS, timeout=20,
        )
        d = r.json()
        if d.get("code") != 0:
            return None
        v = d.get("data") or {}
        pic = (v.get("pic") or "").strip()
        if pic.startswith("http://"):
            pic = pic.replace("http://", "https://", 1)
        return {
            "title": (v.get("title") or "").strip(),
            "owner": ((v.get("owner") or {}).get("name") or "").strip(),
            "bvid": bvid,
            "url": f"https://www.bilibili.com/video/{bvid}",
            "pic": pic,
        }
    except Exception:
        return None


def random_song() -> dict | None:''')
    p.write_text(s, encoding="utf-8")
    print("music.py song_by_bvid 已加")

# 2) 网关 music/share
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "/api/music/share" not in s:
    s = s.replace('@app.get("/api/memory/config")',
'''@app.post("/api/music/share")
async def music_share(token: str = Query(""), payload: dict = None):
    """用户分享一首歌给她，一起听"""
    auth(token)
    body = payload or {}
    text = str(body.get("text", "")).strip()
    if not text:
        return {"ok": False, "error": "empty"}
    m = re.search(r"(BV[0-9A-Za-z]{10})", text)
    song = None
    if m and music is not None:
        song = music.song_by_bvid(m.group(1))
    if not song:
        return {"ok": False, "error": "没识别到 B站 视频链接（需要包含 BV 号）"}
    try:
        system = persona_core.build_system_prompt(life=life_core.current())
        system += (
            f"\\n\\n他给你分享了一首歌：《{song['title']}》（{song['owner']}）。"
            "说一句收到/期待/一起听的话，1-2 句，口语。"
        )
        reply = ask_llm(system, [{"role": "user", "content": f"（分享歌曲：{song['title']}）"}], max_tokens=180)
    except Exception:
        reply = f"收到啦，一起听《{song['title']}》。"
    return {"ok": True, "song": song, "text": reply or "一起听吧"}


@app.get("/api/memory/config")''')
    if "import re" not in s.split("import life_core")[0]:
        s = s.replace("import json\n", "import json\nimport re\n", 1)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("网关 music/share 已加")