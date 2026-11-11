from pathlib import Path
p = Path(r"D:\大肥鱼\docs\交接-安诗鱼App.md")
s = p.read_text(encoding="utf-8")
if "交互约定" not in s:
    s += """

## 十、交互约定（用户明确要求）

**当任务处于"本地模型能力 ≈ 云端模型能力"区间时，必须问用户用本地还是云端，按用户选择执行。**

详见 `docs/交互约定.md`。
- 适用：写代码、短文案、总结、分类、简单问答
- 不适用：长上下文/复杂推理（云端）、仅本地能做的任务（说明原因）
- App 运行时实时聊天回复是否也"每次问"，待用户确认（建议做成设置项）
"""
    p.write_text(s, encoding="utf-8")
    print("handover updated")
else:
    print("already")