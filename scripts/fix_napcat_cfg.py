import json
from pathlib import Path
base = Path(r"D:\大肥鱼\qq\napcat\napcat\config")
for p in base.glob("*.json"):
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        try:
            data = json.loads(raw.decode("utf-8-sig"))
            p.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
            print("fixed BOM:", p.name)
        except Exception as e:
            print("cannot fix", p.name, e)
    else:
        try:
            json.loads(raw.decode("utf-8"))
            print("ok:", p.name)
        except Exception as e:
            print("bad json:", p.name, e)