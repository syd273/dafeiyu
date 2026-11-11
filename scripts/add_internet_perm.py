import json, re
from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\module.json5")
s = p.read_text(encoding="utf-8")
if "ohos.permission.INTERNET" not in s:
    # 在 module 对象内、abilities 前插入 requestPermissions
    s = s.replace('"pages": "$profile:main_pages",',
'''"pages": "$profile:main_pages",
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      }
    ],''')
    p.write_text(s, encoding="utf-8")
    print("INTERNET 权限已添加")
else:
    print("权限已存在")