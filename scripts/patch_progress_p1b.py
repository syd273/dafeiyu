from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P1-b）
1. 抽取 feiyu `tools/brain` 的 episode / facts / recall / affect / consolidate / self 到 `life-core/src/brain`
2. 写 host adapter（思考/反思触发）与 LLM adapter（用户自填 Key，直连）
3. 单测：写入事件 → 回忆检索 → 生成日记
4. 每步用本地 qwen2.5-coder:7b 起草，人工审校，不装第三方依赖""",
"""### P1-b 已完成（2026-11-10）
- `src/brain/episode.mjs`：情景记忆（append-only、规则 gist、情绪极性、显著性）
- `src/brain/recall.mjs`：2-gram 关键词 + 时间衰减（26h 半衰期）+ 显著性/情绪/召回次数加权
- `src/brain/affect.mjs`：情绪状态（valence/arousal/tension）+ 衰减
- `src/brain/self.mjs`：日记生成（LLM 优先，模板兜底）
- `src/adapters/llm.mjs`：OpenAI 兼容直连，Key 用户自填，`LIFE_CORE_NO_LLM=1` 可离线测试
- `src/http.mjs`：新增 GET /recall、GET /diary
- 冒烟测试：
  - 写入 3 条事件 → 检索「好笑的视频」命中第一（0.565）
  - 无 LLM 时日记模板兜底（source=template）
  - 有 Key 时日记由 LLM 生成（source=llm，中文、贴合三条事件）
- 测试后停服、清理数据

### 下一步（P1-c / P2）
1. 抽取 feiyu `facts.mjs`（事实表）与 `intents.mjs`（承诺/打算）到 brain
2. 夜间巩固 `consolidate`：合并同类情景、生成 gist
3. Life Core API 固化 → Python 网关对接（8900）
4. 接 B站/抖音通道（从 feiyu 抽取 tools/lib/bili-*、video.mjs）""")
p.write_text(s, encoding="utf-8")
print("progress updated")