from pathlib import Path
import ast

# 1) 被吵醒后的状态也要带困意
p = Path(r"D:\大肥鱼\persona\persona_core.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''        elif act:
            lines.append(f"【你此刻的状态】你正在{loc}做「{act}」" + (f"（刚发生：{life.get('event')}）" if life.get("event") else "") +
                         "。回复要带一点这个场景的痕迹，不要像专门守着手机聊天。")''',
'''        elif act:
            lines.append(f"【你此刻的状态】你正在{loc}做「{act}」" + (f"（刚发生：{life.get('event')}）" if life.get("event") else "") +
                         "。回复要带一点这个场景的痕迹，不要像专门守着手机聊天。")
            if "被吵醒" in act:
                lines.append("你刚被吵醒，还困着：说话短、迷糊、带困意，别太精神。")''')
p.write_text(s, encoding="utf-8")
ast.parse(s)

# 2) soul 插件：注入调试日志
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_soul\main.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''        req.system_prompt = (req.system_prompt or "") + "\\n\\n" + prompt''',
'''        req.system_prompt = (req.system_prompt or "") + "\\n\\n" + prompt
        try:
            with open(r"D:\\大肥鱼\\logs\\soul_debug.log", "a", encoding="utf-8") as f:
                import time as _t
                f.write(f"[{_t.strftime('%H:%M:%S')}] msg={msg[:30]!r} life={life_state} \\n  prompt_tail={prompt[-260:].replace(chr(10), ' | ')}\\n")
        except Exception:
            pass''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("debug+patch ok")