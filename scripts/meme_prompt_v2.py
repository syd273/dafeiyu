from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''        "\\n\\n【表情包】你习惯在每条回复的最末尾配一张表情，格式：[meme:表情id]。"
        "规则：每次回复都尽量配一张（最多一张）；除非话题非常严肃或你正在生气；"
        "标记必须单独写在回复最后，不要解释它。可用表情：\\n" + "\\n".join(lines)''',
'''        "\\n\\n【表情包】这些是你手机里存着的常用表情，你可以随手发。"
        "在每条回复的最末尾配一张，格式：[meme:表情id]。"
        "规则：每次回复都尽量配一张（最多一张）；话题非常严肃或你正在生气时可以不配；"
        "用户让你发表情时，直接配一张，不要说自己没有表情。"
        "标记必须单独写在回复最后，不要解释它。可用表情：\\n" + "\\n".join(lines)''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("表情提示词已优化")