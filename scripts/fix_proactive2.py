from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_proactive\main.py")
s = p.read_text(encoding="utf-8")
print("occurrences:", s.count('\\\\"'))
s = s.replace('\\\\"', "'")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("syntax ok")