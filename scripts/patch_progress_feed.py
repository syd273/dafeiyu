from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 夜间任务日记同步到她的动态（feed）
2. 上帝视角接入鸿蒙 App
3. 鸿蒙 App 聊天页（等 DevEco Studio）""",
"""### 夜间日记同步动态完成（2026-11-10）
- Life Core `server.mjs` 新增 `appendPersonaFeed(text, emo)`：夜间任务生成日记后写入 `persona/feed.json`（保留 60 条）
- `/nightly/run` 返回 `feedAdded` 标记；`lastNightly.feedAdded` 记录
- 实测：2 条情景 → 夜间任务 → 日记写入 feed 第一条；测试后已恢复原 feed
- 注意：测试前备份 feed、测试后恢复，避免污染真实数据

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. B站/抖音分享接入动态流展示""")
p.write_text(s, encoding="utf-8")
print("progress updated")