from pathlib import Path

# 修复 fmt：兼容秒/毫秒时间戳
p = Path(r"D:\大肥鱼\anshiyu-server\static\godview.html")
s = p.read_text(encoding="utf-8")
old = """function fmt(ts) {
  const d = new Date(ts);"""
new = """function fmt(ts) {
  const ms = ts > 1e12 ? ts : ts * 1000; // feed 用秒，情景用毫秒
  const d = new Date(ms);"""
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("fmt fixed")

# 进度
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. B站/抖音分享接入动态流展示""",
"""### 分享接入动态流完成（2026-11-10）
- 分享（B站/抖音、手动/自动）成功后写入 `persona/feed.json` 动态流
- 上帝视角页新增「她的动态」区块，展示最近 6 条
- 修复：feed 时间戳为秒，页面格式化兼容秒/毫秒
- 截图验证通过（`logs/godview_feed2.png`）

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 主动消息覆盖更多生活场景""")
p.write_text(s, encoding="utf-8")
print("progress updated")