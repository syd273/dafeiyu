from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "import router" not in s:
    s = s.replace("""try:
    import local_llm  # noqa: E402
except Exception:
    local_llm = None""",
"""try:
    import local_llm  # noqa: E402
except Exception:
    local_llm = None
try:
    import router  # noqa: E402
except Exception:
    router = None""")

    # ask_llm 支持 prefer=local 优先
    old = '''def ask_llm(system: str, messages: list[dict], max_tokens: int = 500) -> str:
    body = {'''
    new = '''def ask_llm(system: str, messages: list[dict], max_tokens: int = 500, prefer: str = "auto") -> str:
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
                return local
    body = {'''
    if old in s:
        s = s.replace(old, new)
    else:
        print("MISS ask_llm")

    # 主动消息、分享配文：本地优先
    s = s.replace('(' + chr(10) + '            text = ask_llm(system, [{"role": "user", "content": "（主动发一条）"}], max_tokens=160)',
                  '(' + chr(10) + '            text = ask_llm(system, [{"role": "user", "content": "（主动发一条）"}], max_tokens=200, prefer="local")')
    s = s.replace('text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=160)',
                  'text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200, prefer="local")')

    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("router wired")