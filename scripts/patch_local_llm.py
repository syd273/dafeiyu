from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "local_llm" not in s:
    s = s.replace("""try:
    import douyin  # noqa: E402
except Exception:
    douyin = None""",
"""try:
    import douyin  # noqa: E402
except Exception:
    douyin = None
try:
    import local_llm  # noqa: E402
except Exception:
    local_llm = None""")

    # ask_llm：DeepSeek 失败时，校枢空闲则借本地 qwen3.5:9b
    old = '''    s = requests.Session()
    s.trust_env = False
    r = s.post(API_URL, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()'''
    new = '''    try:
        s = requests.Session()
        s.trust_env = False
        r = s.post(API_URL, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=90)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        # 云端失败：仅当校枢空闲时借用本地 qwen3.5:9b
        if local_llm is not None:
            txt = local_llm.try_local_chat(system, messages, max_tokens=max_tokens)
            if txt:
                return txt
        raise'''
    if old in s:
        s = s.replace(old, new)
        p.write_text(s, encoding="utf-8")
        ast.parse(s)
        print("local fallback integrated")
    else:
        print("MISS")