from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 主动消息覆盖更多生活场景""",
"""### 主动场景扩展完成（2026-11-10）
- `persona/proactive.json` 类型从 9 个扩到 17 个：
  早安 / 早饭 / 午饭 / 下午 / 晚饭 / 晚间 / 晚安 / 周末 / 生活分享 / 媒体分享 / 想到他 / 夸他 / 想念 / 想起旧事 / 生病跟进 / 心情低落 / 吃醋
- 场景条件支持：时间窗、工作日/周末、心情匹配、沉默时长、关键词触发
- 选择方式：条件过滤后按权重随机（不再是取模轮询）
- 新增 `POST /api/proactive/test?type_id=xxx`（测试场景文案，不广播不写库）
- 测试（云端 deepseek-chat 生成）6 个场景全部成功：morning/lunch/night/weekend/mood_care/praise
- 已知问题：生活事件文案重复（"头发翘"）导致主动文案重复，后续需增加事件多样性

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 生活事件池扩充（解决文案重复）""")
p.write_text(s, encoding="utf-8")
print("progress updated")