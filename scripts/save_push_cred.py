import json
from pathlib import Path
cred = {
    "appId": "6917621446672311433",
    "clientId": "6917621446672311433",
    "clientSecret": "66b500a3df0ae4fd12c023acdfde4fa4077e8319320924bf2216ff71b7e44bac",
    "altClientId": "2080778778170102336",
}
p = Path(r"D:\大肥鱼\memory\push_credentials.json")
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(cred, ensure_ascii=False, indent=2), encoding="utf-8")
print("凭据已保存")