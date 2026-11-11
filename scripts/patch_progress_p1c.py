from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P1-c / P2）
1. 抽取 feiyu `facts.mjs`（事实表）与 `intents.mjs`（承诺/打算）到 brain
2. 夜间巩固 `consolidate`：合并同类情景、生成 gist
3. Life Core API 固化 → Python 网关对接（8900）
4. 接 B站/抖音通道（从 feiyu 抽取 tools/lib/bili-*、video.mjs）""",
"""### P1-c 已完成（2026-11-10）
- `src/brain/facts.mjs`：语义事实（无证据不入库、谓词闭集、冲突标 disputed、规则抽取）
- `src/brain/intents.mjs`：前瞻记忆（intent/wish/blocked 三态、10 分钟内去重、done 给正向情绪）
- `src/brain/consolidate.mjs`：巩固（情景→事实/意图，`consolidated.jsonl` 幂等）
- `src/server.mjs`：v0.3，事件写入自动抽意图；新增 /facts /intents /intent/done /consolidate
- 冒烟测试：
  - 事件「我答应明天陪阿东看视频」→ 自动建 intent
  - 巩固 3 条情景 → 2 条事实（累了、番茄炒蛋）+ 1 条意图
  - 二次巩固 processed=0（幂等）
  - /intent/done 标记完成成功
- 本地模型起草 facts 未达标（仅 1745 字符缺实现），已人工重写

### 下一步（P2）
1. Life Core API 固化，写 OpenAPI 风格文档
2. Python 网关（8900）对接 Life Core（转发 /chat /event /state）
3. 接 B站/抖音通道（feiyu tools/lib/bili-*、video.mjs）
4. 上帝视角数据接口（state + episodes + intents + facts 聚合）""")
p.write_text(s, encoding="utf-8")
print("progress updated")