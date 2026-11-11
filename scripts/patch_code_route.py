from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 1) 聊天/内容生成改回云端优先（本地只在云端失败时兜底）
old = '''def ask_llm(system: str, messages: list[dict], max_tokens: int = 500, prefer: str = "auto") -> str:
    # 简单任务优先本地 qwen3.5:9b（校枢空闲时）
    if prefer in ("local", "auto") and local_llm is not None and router is not None:
        text = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                text = m.get("content", "")
                break
        hint = router.pick_provider(text, kind="short_reply" if prefer == "local" else "chat")
        if prefer == "local" or hint == "local":
            local = local_llm.try_local_chat(system, messages, max_tokens=max_tokens)
            if local:
                try:
                    with open(str(BASE / "logs" / "app_llm.log"), "a", encoding="utf-8") as f:
                        f.write(f"[{time.strftime('%H:%M:%S')}] LOCAL | {text[:24]}\\n")
                except Exception:
                    pass
                return local
    body = {'''
new = '''def ask_llm(system: str, messages: list[dict], max_tokens: int = 500, prefer: str = "cloud") -> str:
    """内容生成（聊天/主动消息/分享配文）走云端；本地 qwen3.5:9b 只用于写代码。"""
    body = {'''
if old in s:
    s = s.replace(old, new)
    print("chat reverted to cloud")
else:
    print("MISS revert")

# 2) 主动消息/分享不再要求本地
s = s.replace('max_tokens=200, prefer="local")', 'max_tokens=200)')

# 3) 新增代码生成接口
if "/api/code" not in s:
    s = s.replace('@app.get("/")', '''class CodeIn(BaseModel):
    instruction: str
    context: str = ""
    language: str = ""


@app.post("/api/code")
async def write_code_api(body: CodeIn, token: str = Query("")):
    """写代码交给本地 qwen3.5:9b（校枢空闲时才借）"""
    auth(token)
    try:
        import local_code  # noqa: E402
    except Exception:
        raise HTTPException(status_code=500, detail="local_code not available")
    busy, who = local_llm.gpu_busy() if local_llm is not None else (True, "unavailable")
    if busy:
        return {"ok": False, "reason": "busy", "who": who,
                "hint": "校枢正在使用本地模型，稍后再试或改用云端"}
    code = local_code.write_code(body.instruction, body.context, body.language)
    return {"ok": bool(code), "code": code or ""}


@app.get("/")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("code endpoint added")