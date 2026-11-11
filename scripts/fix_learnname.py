from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_soul\main.py")
s = p.read_text(encoding="utf-8")
old = '''            msg = (event.message_str or "").strip()
            import re as _re
            m = _re.search(r"(?:我叫|我的名字是|我的名字叫|叫我|我是)([\\u4e00-\\u9fa5A-Za-z0-9_]{1,10})", msg)
            if m:
                nm = m.group(1)
                bad = ("学生", "程序员", "打工人", "普通人", "新手", "小白", "本人")
                if nm and nm not in bad and persona is not None:'''
new = '''            msg = (event.message_str or "").strip()
            import re as _re
            m = _re.search(r"(?:我叫|我的名字是|我的名字叫|叫我)([\\u4e00-\\u9fa5A-Za-z0-9_]{1,8})", msg)
            if m:
                nm = m.group(1)
                bad = ("谁", "什么", "你", "我", "他", "她", "学生", "程序员", "打工人",
                       "普通人", "新手", "小白", "本人", "人", "谁啊", "啥")
                if nm and nm not in bad and not _re.search(r"[谁吗呢啊吧]$", nm) and persona is not None:'''
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("learn_name fixed")
else:
    print("MISS")