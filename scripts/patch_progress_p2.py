from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P2）
1. Life Core API 固化，写 OpenAPI 风格文档
2. Python 网关（8900）对接 Life Core（转发 /chat /event /state）
3. 接 B站/抖音通道（feiyu tools/lib/bili-*、video.mjs）
4. 上帝视角数据接口（state + episodes + intents + facts 聚合）""",
"""### P2 进行中（2026-11-10）
- `anshiyu-server/life_core_client.py`：Python 客户端（本地 qwen2.5-coder:7b 起草，人工修正 4 处：围栏/路径/字段/方法）
- `life-core/docs/API.md`：接口文档（本地起草被截断，人工补全）
- 全接口联调通过：health/state/event/chat/recall/consolidate/facts/intents/intent_done/diary

### 下一步（P2 续）
1. Python 网关 8900 接入 Life Core（转发 /chat /event /state，保留 DeepSeek 内容生成）
2. 接 B站/抖音通道（feiyu tools/lib/bili-*、video.mjs）
3. 上帝视角数据接口（state + episodes + intents + facts 聚合）""")
p.write_text(s, encoding="utf-8")
print("progress updated")