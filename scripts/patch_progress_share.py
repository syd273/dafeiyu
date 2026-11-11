from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P3-3）
1. B站/抖音分享加入主动消息循环（定时自主刷+分享）
2. 夜间任务日记同步到她的动态
3. 上帝视角接入鸿蒙 App（Web 组件或原生页）""",
"""### P3-3 主动分享循环完成（2026-11-10）
- `app.py` 新增 `_do_media_share(platform)`：抓取 → LLM 文案 → 写库 → WS 广播 → Life Core event
- proactive 循环新增 `share_media` 类型：
  - 窗口 10:00–22:00
  - 每天最多 2 条分享，间隔 ≥180 分钟（独立限频）
  - 随机 B站/抖音
- 新增 `POST /api/share/auto?platform=bili|douyin|random`（测试/演示）
- `persona/proactive.json` 增加 share_media 类型
- 实测：B站/抖音各触发一次均成功，godview recent 出现 2 条分享经历
- 修复记录：补丁脚本误替换 `import requests as _rq` 导致 3 处缩进损坏，已修复并语法校验通过

### 下一步
1. 夜间任务日记同步到她的动态（feed）
2. 上帝视角接入鸿蒙 App
3. 鸿蒙 App 聊天页（等 DevEco Studio）""")
p.write_text(s, encoding="utf-8")
print("progress updated")