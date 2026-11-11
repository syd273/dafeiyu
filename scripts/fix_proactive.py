from pathlib import Path
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_proactive\main.py")
s = p.read_text(encoding="utf-8")
s = s.replace('cur[\\"location\\"]', "cur['location']")
s = s.replace('cur[\\"activity\\"]', "cur['activity']")
s = s.replace('cur[\\"event\\"]', "cur['event']")
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("syntax ok")