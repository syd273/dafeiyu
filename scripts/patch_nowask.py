from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\persona\persona_core.py")
s = p.read_text(encoding="utf-8")
if "如果阿东问你此刻在干嘛" not in s:
    s = s.replace('''        if life.get("plan_today"):''', '''        if loc or act:
            lines.append("如果阿东问你此刻在干嘛/在做什么，就按上面此刻的状态如实回答，不要答得像在守着他聊天。")
        if life.get("plan_today"):''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("prompt patched")