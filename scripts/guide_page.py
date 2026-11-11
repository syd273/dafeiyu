import json
from pathlib import Path

# 路由
p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
if "pages/Guide" not in d["src"]:
    d["src"].append("pages/Guide")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("路由:", d["src"])

# Index：token 可配置
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("const TOKEN = 'anshiyu-app-2026';", "let TOKEN = 'anshiyu-app-2026';")
s = s.replace("""  async loadConfig() {
    const ctx = getContext(this) as Context;""",
"""  async loadConfig() {
    const ctx = getContext(this) as Context;
    try {
      const custom = await AppConfig.getToken(ctx);
      if (custom) TOKEN = custom;
    } catch (e) { }""")
p.write_text(s, encoding="utf-8")
print("Index token 已支持自定义")

# Settings：token 可配置
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("const TOKEN = 'anshiyu-app-2026';", "let TOKEN = 'anshiyu-app-2026';")
s = s.replace("""  async loadToken() {
    const ctx = getContext(this) as Context;
    this.tokenInput = await AppConfig.getToken(ctx);
  }""",
"""  async loadToken() {
    const ctx = getContext(this) as Context;
    this.tokenInput = await AppConfig.getToken(ctx);
    if (this.tokenInput) TOKEN = this.tokenInput;
  }""")
p.write_text(s, encoding="utf-8")
print("Settings token 已支持自定义")