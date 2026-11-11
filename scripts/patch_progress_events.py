from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 生活事件池扩充（解决文案重复）""",
"""### 生活事件池扩充完成（2026-11-10）
- `persona/life.json` 事件池从 26 条扩到 **73 条**（morning 15 / noon 14 / afternoon 15 / evening 15 / night 14）
- 去掉重复的“头发翘”，新增天气、家务、食物、娱乐、身体、情绪等生活细节
- share_templates 8 条、feed_templates 6 条
- 清除了 `life_state.json` 里旧的事件缓存，重新抽取新事件
- 解决：主动文案反复提“头发翘”的问题

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 主动消息实际运行验证（等待真实触发）""")
p.write_text(s, encoding="utf-8")
print("progress updated")