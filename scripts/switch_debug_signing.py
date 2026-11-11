from pathlib import Path
p = Path(r"D:\anshiyu_app\build-profile.json5")
s = p.read_text(encoding="utf-8")
s = s.replace('"signingConfig": "release"', '"signingConfig": "default"')
p.write_text(s, encoding="utf-8")
print("products 已切回 default（debug）")