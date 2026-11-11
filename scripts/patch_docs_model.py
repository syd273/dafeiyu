from pathlib import Path

p = Path(r"D:\大肥鱼\docs\项目边界-不与校枢冲突.md")
s = p.read_text(encoding="utf-8")
if "写代码" not in s:
    s += """

## 六、模型分工（用户确认版）

| 用途 | 模型 | 说明 |
|---|---|---|
| 聊天/主动消息/分享配文的**内容生成** | **DeepSeek 云端** | 不走本地，避免内容质量下降 |
| **写代码**（开发任务） | **本地 qwen3.5:9b**（校枢空闲时） | 用户明确：写相关代码时交给它 |

实现：
- 内容：`app.py` 的 `ask_llm(prefer="cloud")` 默认云端
- 写代码：
  - HTTP：`POST /api/code {"instruction": "...", "context": "...", "language": "python"}`
  - 命令行：`python local_code.py "写一个..." [上下文文件]`
  - 均先查 Ollama 是否空闲；校枢占用时返回 `busy`，绝不抢占
  - qwen3.5:9b 为思考模型，已设 `think=false`

实测：
- 校枢忙时：`/api/code` 返回 `{"ok": false, "reason": "busy"}`
- 校枢空闲时：生成成功（回文函数示例）
"""
    p.write_text(s, encoding="utf-8")
    print("boundary updated")

p = Path(r"D:\大肥鱼\docs\交接-安诗鱼App.md")
s = p.read_text(encoding="utf-8")
if "写代码" not in s:
    s += """

## 九、模型分工约定（2026-11-07 用户确认）

- 聊天/主动消息/分享内容 → **DeepSeek 云端**
- 写代码任务 → **本地 qwen3.5:9b**（仅校枢空闲时，经 `local_llm.py` 借调）
  - HTTP：`POST /api/code`
  - CLI：`python local_code.py`
- 校枢占用时一律不借调，返回 busy
"""
    p.write_text(s, encoding="utf-8")
    print("handover updated")