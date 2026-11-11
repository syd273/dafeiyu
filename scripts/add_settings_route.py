import json
from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
if "pages/Settings" not in d["src"]:
    d["src"].append("pages/Settings")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Settings 页已注册")
else:
    print("已存在")