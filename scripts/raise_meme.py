from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''        "\\n\\n【表情包】你可以在回复的最末尾加一个表情标记，格式：[meme:表情id]。"
        "规则：一次回复最多一个；只在轻松、开心、调侃、安慰时用；严肃话题不用；"
        "标记必须单独写在回复最后，不要解释它。可用表情：\\n" + "\\n".join(lines)''',
'''        "\\n\\n【表情包】你习惯在每条回复的最末尾配一张表情，格式：[meme:表情id]。"
        "规则：每次回复都尽量配一张（最多一张）；除非话题非常严肃或你正在生气；"
        "标记必须单独写在回复最后，不要解释它。可用表情：\\n" + "\\n".join(lines)''')
s = s.replace("if random.random() > 0.5:\n            return reply",
              "if random.random() > 0.85:\n            return reply")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("频率已提高")