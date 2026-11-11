from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P2 续）
1. Python 网关 8900 接入 Life Core（转发 /chat /event /state，保留 DeepSeek 内容生成）
2. 接 B站/抖音通道（feiyu tools/lib/bili-*、video.mjs）
3. 上帝视角数据接口（state + episodes + intents + facts 聚合）""",
"""### P2 网关接入完成（2026-11-10）
- `anshiyu-server/life_bridge.py`：Life Core 桥接（同步、8s 超时、失败降级为空）
  - 本地起草版本把同步客户端误当异步、方法名不匹配 → 人工重写
- `anshiyu-server/app.py` 新增：
  - `GET /api/life/state`
  - `POST /api/life/event`
  - `GET /api/godview`（生活状态 + 最近情景 + 意图 + 事实聚合）
- 联调通过：网关 8900 ↔ Life Core 8910，event 写入、godview 聚合正常
- 测试后停服、清理数据

### 下一步（P3）
1. 上帝视角前端页（读 /api/godview，状态面板 + 时间轴 + 最近情景 + 意图）
2. B站/抖音通道抽取（feiyu tools/lib/bili-*、video.mjs），接 /api/share/*
3. Life Core 夜间巩固定时任务（每晚一次 consolidate + diary）""")
p.write_text(s, encoding="utf-8")
print("progress updated")