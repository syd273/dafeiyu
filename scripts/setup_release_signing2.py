from pathlib import Path
p = Path(r"D:\anshiyu_app\build-profile.json5")
s = p.read_text(encoding="utf-8")

if '"certpath": "D:\\\\大肥鱼\\\\signing' not in s:
    s = s.replace('''    "signingConfigs": [
      {
        "name": "default",''',
'''    "signingConfigs": [
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
      },
      {
        "name": "default",''')
    s = s.replace('"signingConfig": "default"', '"signingConfig": "release"')
    p.write_text(s, encoding="utf-8")
    print("release 签名已配置")
else:
    print("已配置")