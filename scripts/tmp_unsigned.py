from pathlib import Path
import re
p = Path(r"D:\anshiyu_app\build-profile.json5")
s = p.read_text(encoding="utf-8")
# 移除 signingConfigs 数组
s = re.sub(r'"signingConfigs":\s*\[.*?\n    \],\n', '', s, flags=re.S)
# 移除 products 里的 signingConfig 行
s = re.sub(r'"signingConfig":\s*"[^"]*",\n', '', s)
p.write_text(s, encoding="utf-8")
print("签名配置已临时移除")