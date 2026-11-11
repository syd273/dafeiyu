from pathlib import Path
import ast

# ===== 1) Index 启动时注册 Push token =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { Notifier } from '../common/Notifier';",
"""import { Notifier } from '../common/Notifier';
import { PushHelper } from '../common/PushHelper';""")
s = s.replace("""    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
      this.finishSplash();
    }).catch(() => { this.finishSplash(); });""",
"""    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
      this.finishSplash();
      PushHelper.register(this.baseUrl);
    }).catch(() => { this.finishSplash(); });""")
p.write_text(s, encoding="utf-8")
print("Index 已接入 PushHelper")

# ===== 2) 网关：保存 token + 推送发送 =====
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "/api/push/token" not in s:
    s = s.replace('PUSH_LOG = BASE / "memory" / "push_log.jsonl"',
'''PUSH_LOG = BASE / "memory" / "push_log.jsonl"
PUSH_TOKEN_FILE = BASE / "memory" / "push_token.json"
PUSH_CRED_FILE = BASE / "memory" / "push_credentials.json"


def _push_token() -> str:
    try:
        return str(json.loads(PUSH_TOKEN_FILE.read_text(encoding="utf-8")).get("pushToken", ""))
    except Exception:
        return ""


def _push_credentials() -> dict:
    try:
        return json.loads(PUSH_CRED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _send_hw_push(title: str, text: str) -> bool:
    """调用华为 Push Kit 发通知（需要 AGC 凭据）"""
    cred = _push_credentials()
    app_id = str(cred.get("appId", ""))
    client_id = str(cred.get("clientId", ""))
    client_secret = str(cred.get("clientSecret", ""))
    token = _push_token()
    if not (app_id and client_id and client_secret and token):
        return False
    try:
        # 1) 获取 access token
        tr = requests.post(
            "https://oauth-login.cloud.huawei.com/oauth2/v3/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15,
            proxies={"http": None, "https": None},
        )
        access = tr.json().get("access_token", "")
        if not access:
            return False
        # 2) 发送通知
        body = {
            "validate_only": False,
            "message": {
                "notification": {"title": title, "body": text},
                "token": [token],
            },
        }
        r = requests.post(
            f"https://push-api.cloud.huawei.com/v1/{app_id}/messages:send",
            headers={"Authorization": f"Bearer {access}", "Content-Type": "application/json; charset=UTF-8"},
            json=body,
            timeout=15,
            proxies={"http": None, "https": None},
        )
        return r.status_code == 200
    except Exception:
        return False''')

    s = s.replace('@app.get("/api/music/recommend")',
'''@app.post("/api/push/token")
async def push_token_register(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    pt = str(body.get("pushToken", "")).strip()
    if not pt:
        return {"ok": False, "error": "empty token"}
    PUSH_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUSH_TOKEN_FILE.write_text(json.dumps({"pushToken": pt}, ensure_ascii=False), encoding="utf-8")
    return {"ok": True}


@app.get("/api/push/status")
async def push_status(token: str = Query("")):
    auth(token)
    cred = _push_credentials()
    return {
        "ok": True,
        "hasToken": bool(_push_token()),
        "hasCredentials": bool(cred.get("appId") and cred.get("clientId") and cred.get("clientSecret")),
    }


@app.post("/api/push/send")
async def push_send(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    title = str(body.get("title", "安诗鱼"))
    text = str(body.get("text", ""))
    ok = _send_hw_push(title, text)
    return {"ok": ok}


@app.get("/api/music/recommend")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("网关 Push 接口已加")
else:
    print("已存在")