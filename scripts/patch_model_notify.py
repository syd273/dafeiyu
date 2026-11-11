from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发铁律.md")
s = p.read_text(encoding="utf-8")
if "告知模型" not in s:
    s = s.replace("## 6. 语言：中文", """## 6. 模型调用必须告知

- 每次调用模型（本地或云端）都要**明确告知所用模型名**
- 例：「用本地 qwen2.5-coder:7b 起草」「用云端 deepseek-chat 生成日记」
- 调用结果也要说明：哪个模型、耗时、是否达标、是否人工修正

## 7. 语言：中文""")
    p.write_text(s, encoding="utf-8")
    print("rule added")

p = Path(r"D:\大肥鱼\docs\交互约定.md")
s = p.read_text(encoding="utf-8")
if "告知模型" not in s:
    s += "\n## 7. 模型调用告知\n\n每次调用模型（本地/云端）都必须告诉用户：模型名、用途、结果（达标/重写）。\n"
    p.write_text(s, encoding="utf-8")
    print("interaction updated")