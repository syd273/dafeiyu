from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 把主动消息记录同步到上帝视角动态流""",
"""### 主动消息同步动态流完成（2026-11-10）
- `proactive_loop` 生成主动消息后写入 `persona/feed.json`（动态流）
- 上帝视角「她的动态」自动展示（每 10s 刷新）
- 实测：WS 监听 4 分钟收到主动消息
  `阿东，我这边天阴沉沉的，感觉随时要下雨。你在外面的话记得带伞啊。`
  且 feed 第一条即为该消息
- 生成模型：云端 deepseek-chat
- 验证后清理：测试消息/记忆星已删、app_state 与 feed 已恢复

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 主动消息/分享统一在动态流中分类展示""")
p.write_text(s, encoding="utf-8")
print("progress updated")