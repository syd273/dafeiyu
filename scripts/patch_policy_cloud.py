import json
from pathlib import Path

# 1) 配置：App 聊天策略 = 云端优先
p = Path(r"D:\大肥鱼\anshiyu-server\config.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["chat_provider_policy"] = "cloud_first"   # cloud_first | local_first | ask
d["local_fallback_on_cloud_fail"] = True
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("config ok:", d.get("chat_provider_policy"))

# 2) 文档：记录用户选择
p = Path(r"D:\大肥鱼\docs\交互约定.md")
s = p.read_text(encoding="utf-8")
s = s.replace("- App 运行时的实时聊天回复：是否也要\"每次问\"？（不现实，建议给 App 加设置项：云端优先/本地优先/每次都问）",
              "- ✅ 已确认（2026-11-09）：**App 实时聊天 = 云端优先**；云端失败才切本地（校枢空闲时）\n- 开发任务（写代码/短文案等两边都能做）：仍然每次问用户")
p.write_text(s, encoding="utf-8")
print("interaction doc updated")

# 3) 交接文档同步
p = Path(r"D:\大肥鱼\docs\交接-安诗鱼App.md")
s = p.read_text(encoding="utf-8")
s = s.replace("- App 运行时实时聊天回复是否也\"每次问\"，待用户确认（建议做成设置项）",
              "- ✅ 已确认：App 实时聊天 = **云端优先**（cloud_first），云端失败才本地兜底；开发任务仍每次问用户")
p.write_text(s, encoding="utf-8")
print("handover updated")