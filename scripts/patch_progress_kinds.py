from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 主动消息/分享统一在动态流中分类展示""",
"""### 动态流分类展示完成（2026-11-10）
- feed 条目增加 `kind` 字段：`talk`（说说）/ `share`（分享）/ `proactive`（主动消息）/ `diary`（日记）
- 写入点已接入：
  - 分享（B站/抖音）→ share
  - 主动消息 → proactive
  - 夜间日记 → diary
  - 日常说说 → talk（默认）
- 上帝视角「她的动态」增加彩色标签与筛选按钮（全部/说说/分享/主动/日记）
- 兼容旧条目（无 kind 视为说说）
- 截图验证通过（`logs/godview_kinds.png`）
- 本轮未调用模型

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 动态流数据接入星图 App 展示""")
p.write_text(s, encoding="utf-8")
print("progress updated")