from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "\nimport re\n" not in s:
    s = s.replace("import json\n", "import json\nimport re\n", 1)
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("re 已导入")