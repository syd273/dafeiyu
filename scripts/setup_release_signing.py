import json
from pathlib import Path

p = Path(r"D:\anshiyu_app\build-profile.json5")
s = p.read_text(encoding="utf-8")

# 在 signingConfigs 开头插入 release 配置
if '"name": "release"' not in s:
    s = s.replace('"signingConfigs": [',
'''"signingConfigs": [
    {
      "name": "release",
      "type": "HarmonyOS",
      "material": {
        "certpath": "D:\\\\大肥鱼\\\\signing\\\\anshiyu.cer",
        "keyAlias": "anshiyu",
        "keyPassword": "Anshiyu2026!",
        "profile": "D:\\\\大肥鱼\\\\signing\\\\anshiyu.p7b",
        "signAlg": "SHA256withECDSA",
        "storeFile": "D:\\\\大肥鱼\\\\signing\\\\anshiyu.p12",
        "storePassword": "Anshiyu2026!"
      }
    },''')
    # products 指向 release
    s = s.replace('"signingConfig": "default"', '"signingConfig": "release"')
    p.write_text(s, encoding="utf-8")
    print("已配置 release 签名")
else:
    print("已存在")