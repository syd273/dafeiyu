from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/share/config" not in s:
    s = s.replace('MEMORY_STARS = BASE / "milky-way-3d" / "memory_stars.json"',
'''MEMORY_STARS = BASE / "milky-way-3d" / "memory_stars.json"
SHARE_CFG = BASE / "persona" / "share_config.json"


def _share_platform() -> str:
    try:
        d = json.loads(SHARE_CFG.read_text(encoding="utf-8"))
        v = str(d.get("platform", "both"))
        return v if v in ("bili", "douyin", "both") else "both"
    except Exception:
        return "both"


def _pick_platform() -> str:
    p = _share_platform()
    if p == "both":
        return random.choice(["bili", "douyin"])
    return p''')

    s = s.replace('@app.get("/api/messages/recent")',
'''@app.get("/api/share/config")
async def get_share_config(token: str = Query("")):
    auth(token)
    return {"ok": True, "platform": _share_platform()}


@app.post("/api/share/config")
async def set_share_config(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    p = str(body.get("platform", "both"))
    if p not in ("bili", "douyin", "both"):
        return {"ok": False, "error": "invalid platform"}
    SHARE_CFG.parent.mkdir(parents=True, exist_ok=True)
    SHARE_CFG.write_text(json.dumps({"platform": p}, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "platform": p}


@app.get("/api/messages/recent")''')

    # share_auto 使用配置
    s = s.replace('    kind = platform if platform in ("bili", "douyin") else random.choice(["bili", "douyin"])',
                  '    kind = platform if platform in ("bili", "douyin") else _pick_platform()')
    # 主动分享使用配置
    s = s.replace('''            platform = random.choice(["bili", "douyin"])
            res = await _do_media_share(platform)''',
'''            platform = _pick_platform()
            res = await _do_media_share(platform)''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("分享平台配置已加")
else:
    print("已存在")