from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\local_llm.py")
s = p.read_text(encoding="utf-8")
s = s.replace('KEEP_ALIVE = "60s"', 'KEEP_ALIVE = "30s"')
s = s.replace('''        body = {
            "model": MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "keep_alive": KEEP_ALIVE,
            "options": {"temperature": 0.9, "num_predict": max_tokens, "num_ctx": 4096},
        }''',
'''        body = {
            "model": MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "think": False,          # qwen3.5 是思考模型，关掉思考否则 content 为空
            "keep_alive": KEEP_ALIVE,
            "options": {"temperature": 0.9, "num_predict": max_tokens, "num_ctx": 4096},
        }''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("local_llm patched (think=False, 30s)")