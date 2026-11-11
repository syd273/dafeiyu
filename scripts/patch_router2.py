from pathlib import Path
import ast

# 1) 扩充复杂关键词
p = Path(r"D:\大肥鱼\anshiyu-server\router.py")
s = p.read_text(encoding="utf-8")
s = s.replace('    "医院", "吃药", "难受", "委屈", "想放弃", "迷茫",',
              '    "医院", "吃药", "难受", "委屈", "想放弃", "迷茫",\n    "重写", "总结", "概括", "复盘", "记忆", "梳理", "写一段", "生成", "翻译",')
p.write_text(s, encoding="utf-8")

# 2) app.py 记录用了哪个模型
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "app_llm.log" not in s:
    s = s.replace('''            local = local_llm.try_local_chat(system, messages, max_tokens=max_tokens)
            if local:
                return local''',
'''            local = local_llm.try_local_chat(system, messages, max_tokens=max_tokens)
            if local:
                try:
                    with open(str(BASE / "logs" / "app_llm.log"), "a", encoding="utf-8") as f:
                        f.write(f"[{time.strftime('%H:%M:%S')}] LOCAL | {text[:24]}\\n")
                except Exception:
                    pass
                return local''')
    s = s.replace('''        return r.json()["choices"][0]["message"]["content"].strip()''',
'''        out = r.json()["choices"][0]["message"]["content"].strip()
        try:
            with open(str(BASE / "logs" / "app_llm.log"), "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] CLOUD | {out[:24]}\\n")
        except Exception:
            pass
        return out''', 1)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("logging added")