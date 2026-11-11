import json
from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\module.json5")
s = p.read_text(encoding="utf-8")
if "backgroundModes" not in s:
    s = s.replace('''        "exported": true,
        "skills": [''',
'''        "exported": true,
        "backgroundModes": [
          "dataTransfer"
        ],
        "skills": [''')
    p.write_text(s, encoding="utf-8")
    print("backgroundModes 已加")
else:
    print("已存在")