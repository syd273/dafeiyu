import json
from pathlib import Path

# 1) 应用名称
p = Path(r"D:\anshiyu_app\AppScope\resources\base\element\string.json")
d = json.loads(p.read_text(encoding="utf-8"))
for item in d["string"]:
    if item["name"] == "app_name":
        item["value"] = "安诗鱼"
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("app_name = 安诗鱼")

p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\element\string.json")
d = json.loads(p.read_text(encoding="utf-8"))
m = {"module_desc": "安诗鱼聊天", "EntryAbility_desc": "和安诗鱼聊天", "EntryAbility_label": "安诗鱼"}
for item in d["string"]:
    if item["name"] in m:
        item["value"] = m[item["name"]]
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("entry strings 已中文化")

# 2) BASE 改为电脑局域网 IP
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("// 连接本地网关（默认 http://127.0.0.1:8900）\n// 真机使用时把 BASE 改成电脑的局域网 IP（例如 http://192.168.11.5:8900）",
              "// 连接本地网关（真机通过局域网访问电脑的 8900 端口）\n// 电脑 IP 变化时只需改这一行")
s = s.replace("const BASE = 'http://127.0.0.1:8900';", "const BASE = 'http://192.168.43.5:8900';")
p.write_text(s, encoding="utf-8")
print("BASE = http://192.168.43.5:8900")