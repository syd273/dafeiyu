from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\persona\persona_core.py")
s = p.read_text(encoding="utf-8")
old = '''        elif act:
            lines.append(f"【你此刻的状态】你正在{loc}做「{act}」" + (f"（刚发生：{life.get('event')}）" if life.get("event") else "") +
                         "。回复要带一点这个场景的痕迹，不要像专门守着手机聊天。")
            if life.get("plan_today"):
                lines.append("【你今天的安排】" + "；".join(life["plan_today"]))
            if life.get("plan_tomorrow"):
                lines.append("【你明天的安排】" + "；".join(life["plan_tomorrow"]))
            if "被吵醒" in act:
                lines.append("你刚被吵醒，还困着：说话短、迷糊、带困意，别太精神。")'''
new = '''        elif act:
            lines.append(f"【你此刻的状态】你正在{loc}做「{act}」" + (f"（刚发生：{life.get('event')}）" if life.get("event") else "") +
                         "。回复要带一点这个场景的痕迹，不要像专门守着手机聊天。")
            if "被吵醒" in act:
                lines.append("你刚被吵醒，还困着：说话短、迷糊、带困意，别太精神。")
        if life.get("plan_today"):
            lines.append("【你今天的安排】" + "；".join(life["plan_today"]))
        if life.get("plan_tomorrow"):
            lines.append("【你明天的安排】" + "；".join(life["plan_tomorrow"]))
        if life.get("plan_today") or life.get("plan_tomorrow"):
            lines.append("如果阿东问起你明天/今天有没有空、有没有事，就按上面的安排自然地回答；"
                         "没写在安排里的事，就说不确定/还没想好，别编。")'''
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("plans injection fixed")
else:
    print("MISS")