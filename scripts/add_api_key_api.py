from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/config/api-key" not in s:
    s = s.replace("import json\nimport re\n", "import json\nimport re\nimport subprocess\n", 1)
    s = s.replace('@app.get("/api/memory/config")',
'''def _mask_key(key: str) -> str:
    k = (key or "").strip()
    if len(k) < 12:
        return "已配置" if k else ""
    return k[:6] + "…" + k[-4:]


def _harden_key_file(path: Path) -> None:
    """Windows ACL：只允许当前用户访问 key 文件"""
    try:
        user = os.environ.get("USERNAME", "")
        if not user:
            return
        subprocess.run(
            ["icacls", str(path), "/inheritance:r", "/grant:r", f"{user}:F"],
            capture_output=True, timeout=10,
        )
    except Exception:
        pass


@app.get("/api/config/api-key")
async def get_api_key(token: str = Query("")):
    auth(token)
    return {"ok": True, "configured": bool(KEY), "masked": _mask_key(KEY)}


@app.post("/api/config/api-key")
async def set_api_key(token: str = Query(""), payload: dict = None):
    auth(token)
    global KEY
    body = payload or {}
    key = str(body.get("apiKey", "")).strip()
    if not key.startswith("sk-") or len(key) < 20:
        return {"ok": False, "error": "格式不对：应以 sk- 开头"}
    try:
        target = Path(CFG["deepseek_key_file"])
        target.write_text(key, encoding="utf-8")
        _harden_key_file(target)
        KEY = key
        return {"ok": True, "masked": _mask_key(key)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/config/api-key/test")
async def test_api_key(token: str = Query("")):
    auth(token)
    if not KEY:
        return {"ok": False, "error": "未配置"}
    try:
        r = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            json={"model": CFG.get("model", "deepseek-chat"),
                  "messages": [{"role": "user", "content": "hi"}],
                  "max_tokens": 1},
            timeout=25,
            proxies={"http": None, "https": None},
        )
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/api/memory/config")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("API Key 接口已加")
else:
    print("已存在")