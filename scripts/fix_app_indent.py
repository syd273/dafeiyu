from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
bad = "import random\nimport requests as _rq"
fixed = s.replace(bad, "import requests as _rq")
print("修复处数:", s.count(bad))
p.write_text(fixed, encoding="utf-8")
ast.parse(fixed)
print("语法 OK")