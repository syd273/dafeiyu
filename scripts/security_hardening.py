from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 1) 关闭文档 + 收紧 CORS
s = s.replace('app = FastAPI(title="Anshiyu Server")',
              'app = FastAPI(title="Anshiyu Server", docs_url=None, redoc_url=None, openapi_url=None)')
s = s.replace('''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],''',
'''app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8899", "http://localhost:8899", "null"],''')

# 2) token 比较防时序
s = s.replace('''def auth(token: str | None):
    if token != CFG.get("token"):
        raise HTTPException(status_code=401, detail="bad token")''',
'''_AUTH_FAILS: dict[str, list[float]] = {}


def _client_key(request: Request) -> str:
    try:
        return request.client.host if request.client else "unknown"
    except Exception:
        return "unknown"


def auth(token: str | None):
    import hmac
    expect = str(CFG.get("token", ""))
    if not token or not hmac.compare_digest(str(token), expect):
        raise HTTPException(status_code=401, detail="bad token")


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """简单限流：每个 IP 每分钟最多 120 次请求"""
    key = _client_key(request)
    now = time.time()
    arr = _AUTH_FAILS.setdefault(key, [])
    arr[:] = [t for t in arr if now - t < 60]
    if len(arr) >= 120:
        from fastapi.responses import JSONResponse
        return JSONResponse({"ok": False, "error": "too many requests"}, status_code=429)
    arr.append(now)
    return await call_next(request)''')

# 3) 功能开关
s = s.replace('''@app.get("/api/legacy/status")''',
'''DEFAULT_FEATURES = {"room": True, "stickers": True, "trends": True}


def _features() -> dict:
    try:
        f = CFG.get("features") or {}
        return {**DEFAULT_FEATURES, **f}
    except Exception:
        return dict(DEFAULT_FEATURES)


@app.get("/api/features")
async def get_features(token: str = Query("")):
    auth(token)
    return {"ok": True, **_features()}


@app.post("/api/features")
async def set_features(token: str = Query(""), payload: dict = None):
    auth(token)
    body = payload or {}
    cur = _features()
    for k in ("room", "stickers", "trends"):
        if k in body:
            cur[k] = bool(body[k])
    CFG["features"] = cur
    try:
        (SERVER_DIR / "config.json").write_text(json.dumps(CFG, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return {"ok": True, **cur}


@app.get("/api/legacy/status")''')

# 4) chat 中按开关注入表情/热点
s = s.replace("""        if trends is not None:
            system_prompt += trends.prompt_block()""",
"""        if trends is not None and _features().get("trends", True):
            system_prompt += trends.prompt_block()""")
s = s.replace("""    try:
        system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()""",
"""    try:
        if _features().get("stickers", True):
            system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()""")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("安全加固与开关已加")