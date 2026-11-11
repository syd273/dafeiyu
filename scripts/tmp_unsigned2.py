from pathlib import Path
import re
p = Path(r"D:\anshiyu_app\build-profile.json5")
s = p.read_text(encoding="utf-8")
s = re.sub(r'"signingConfigs":\s*\[.*?\n    \],\n', '', s, flags=re.S)
s = re.sub(r'"signingConfig":\s*"[^"]*",\n', '', s)
p.write_text(s, encoding="utf-8")
print("已移除签名配置")