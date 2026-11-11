from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P3-1）
1. 上帝视角前端页（读 /api/godview：状态面板 + 时间轴 + 最近情景 + 意图 + 事实）
2. Life Core 夜间巩固定时任务（每晚 consolidate + diary）
3. B站/抖音分享加入主动消息循环（定时自主刷+分享）""",
"""### P3-2b 记忆完全模式 + 夜间巩固完成（2026-11-10）
- `life-core/src/config.mjs`：运行选项 `memoryMode: decay | full`、夜间时间
- 记忆完全模式（full）：
  - 情景全量常驻内存（`cached` 计数可查）
  - 召回不做时间衰减（recency 权重归零），最多返回 50 条
  - 不降低记忆强度
- 夜间巩固：
  - 定时任务（默认每天 03:30，按 options 配置）自动 consolidate + diary
  - 手动触发 `POST /nightly/run`
  - `state.lastNightly` 记录时间与结果
- 网关新增：`GET/POST /api/memory/mode`、`POST /api/nightly/run`、`/api/godview` 返回 memoryMode
- 实测：
  - 8 条事件 → 切 full → 全量召回 8 条、cached=8
  - 夜间任务 processed=8、factsAdded=1、intentsAdded=1、diary=template
  - 切回 decay 正常

### 下一步（P3-1）
1. 上帝视角前端页（读 /api/godview：状态面板 + 时间轴 + 最近情景 + 意图 + 事实 + 记忆模式开关）
2. B站/抖音分享加入主动消息循环（定时自主刷+分享）
3. 夜间任务结果写日记并同步到动态""")
p.write_text(s, encoding="utf-8")
print("progress updated")