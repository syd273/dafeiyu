import json, re
from pathlib import Path
src = Path(r"D:\大肥鱼\research\dsh-meme\src\catalog.ts").read_text(encoding="utf-8")
pat = re.compile(r"\{ id: '([^']+)', text: '([^']+)', file: '([^']+)', tone: '([^']+)' \}")
items = []
for m in pat.finditer(src):
    items.append({"id": m.group(1), "text": m.group(2), "file": m.group(3), "tone": m.group(4)})
out = Path(r"D:\大肥鱼\persona\stickers.json")
out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print("清单条数:", len(items))