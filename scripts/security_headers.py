from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "X-Content-Type-Options" not in s:
    s = s.replace('''@app.middleware("http")
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
    return await call_next(request)''',
'''@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """限流 + 请求体大小限制 + 安全响应头"""
    from fastapi.responses import JSONResponse
    key = _client_key(request)
    now = time.time()
    arr = _AUTH_FAILS.setdefault(key, [])
    arr[:] = [t for t in arr if now - t < 60]
    if len(arr) >= 120:
        return JSONResponse({"ok": False, "error": "too many requests"}, status_code=429)
    arr.append(now)
    # 请求体大小限制（2MB）
    try:
        cl = int(request.headers.get("content-length") or 0)
        if cl > 2 * 1024 * 1024:
            return JSONResponse({"ok": False, "error": "payload too large"}, status_code=413)
    except Exception:
        pass
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("响应头与大小限制已加")