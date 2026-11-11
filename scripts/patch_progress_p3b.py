from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P3）
1. 上帝视角前端页（读 /api/godview，状态面板 + 时间轴 + 最近情景 + 意图）
2. B站/抖音通道抽取（feiyu tools/lib/bili-*、video.mjs），接 /api/share/*
3. Life Core 夜间巩固定时任务（每晚一次 consolidate + diary）""",
"""### P3-2 媒体通道完成（2026-11-10）
- 确认：feiyu 的 `video.mjs` 是视频剪辑（ffmpeg），不是刷 B 站；抓取直接复用已有 `persona/bili.py`、`persona/douyin.py`
- `anshiyu-server/app.py` 的 `/api/share/bili`、`/api/share/douyin` 已接入 Life Core：
  - 抓取 → LLM 生成分享文案 → 写入 `life_bridge.event("share", ...)` → 返回 + WS 广播
- 联调通过：
  - B站：生成文案 + 链接，life_core=True
  - 抖音：生成文案 + 链接，life_core=True
  - `/api/godview` 的 recent 出现 2 条分享经历

### 下一步（P3-1）
1. 上帝视角前端页（读 /api/godview：状态面板 + 时间轴 + 最近情景 + 意图 + 事实）
2. Life Core 夜间巩固定时任务（每晚 consolidate + diary）
3. B站/抖音分享加入主动消息循环（定时自主刷+分享）""")
p.write_text(s, encoding="utf-8")
print("progress updated")