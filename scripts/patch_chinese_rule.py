from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发铁律.md")
s = p.read_text(encoding="utf-8")
if "中文呈现" not in s:
    s = s.replace("## 6. 变更原则", """## 6. 语言：中文

- 我的思考过程、解释、日志说明**一律用中文呈现**
- Life Core 的思考/反思/日记/记忆内容用中文生成
- 代码注释用中文

## 7. 变更原则""")
    p.write_text(s, encoding="utf-8")
    print("rule added")

p = Path(r"D:\大肥鱼\docs\交互约定.md")
s = p.read_text(encoding="utf-8")
if "中文呈现" not in s:
    s += "\n## 6. 语言\n\n思考过程、解释、日志、代码注释一律用中文呈现。\n"
    p.write_text(s, encoding="utf-8")
    print("interaction updated")