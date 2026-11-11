from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace("""    # 表情包引导（追加到系统提示）
    try:
        system = ask_system_with_meme(system)
    except Exception:
        pass
    mood = persona_core.current_mood().get("mood", "平静")""",
"""    # 表情包引导（追加到系统提示）
    try:
        system_prompt = ask_system_with_meme(system_prompt)
    except Exception:
        pass
    mood = persona_core.current_mood().get("mood", "平静")""")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("变量名已修复")