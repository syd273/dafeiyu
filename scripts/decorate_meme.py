from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "_decorate_meme" not in s:
    s = s.replace('''def ask_system_with_meme(system: str) -> str:''',
'''MEME_BY_MOOD = {
    "开心": ["daily-chat", "great-question", "enough"],
    "兴奋": ["great-question", "deep-thought"],
    "平静": ["daily-chat", "deep-thought"],
    "着急": ["not-stuck", "thinking-stopped"],
    "担心": ["not-stuck", "memory-alive"],
    "生气": ["no-thanks", "enough"],
    "累了": ["fish-philosophy", "thinking-stopped"],
    "吃醋": ["no-thanks", "human-questions"],
}


def _decorate_meme(reply: str, mood: str) -> str:
    """模型没配表情时，按情绪随机补一张（约一半概率）"""
    try:
        if "[meme:" in reply:
            return reply
        if random.random() > 0.5:
            return reply
        pool = MEME_BY_MOOD.get(mood, ["daily-chat"])
        return reply.rstrip() + f" [meme:{random.choice(pool)}]"
    except Exception:
        return reply


def ask_system_with_meme(system: str) -> str:''')

    s = s.replace('''    mood = persona_core.current_mood().get("mood", "平静")
    # 注意：聊天回复通过 HTTP 返回，不再 WS 广播，避免 App 重复显示''',
'''    mood = persona_core.current_mood().get("mood", "平静")
    reply = _decorate_meme(reply, mood)
    # 注意：聊天回复通过 HTTP 返回，不再 WS 广播，避免 App 重复显示''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("情绪配表情已加")