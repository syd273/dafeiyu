from pathlib import Path
import ast

# 1) 网关：聊天回复只走 HTTP 返回，不再 WS 广播（避免 App 收到两遍）
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
old = '''    mood = persona_core.current_mood().get("mood", "平静")
    await broadcast({"type": "message", "role": "assistant", "text": reply, "ts": int(time.time())})
    return {"reply": reply, "mood": mood, "life": life_core.current()}'''
new = '''    mood = persona_core.current_mood().get("mood", "平静")
    # 注意：聊天回复通过 HTTP 返回，不再 WS 广播，避免 App 重复显示
    return {"reply": reply, "mood": mood, "life": life_core.current()}'''
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("gateway dupe fixed")
else:
    print("gateway MISS")

# 2) App：防御性去重（相同内容 3 秒内不重复显示）
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace('''  private ws: webSocket.WebSocket | null = null;
  private scroller: Scroller = new Scroller();''',
'''  private ws: webSocket.WebSocket | null = null;
  private scroller: Scroller = new Scroller();
  private lastAssistant: string = '';
  private lastAssistantTs: number = 0;''')
s = s.replace('''  addMessage(role: string, text: string) {
    this.messages.push({ role: role, text: text, ts: Date.now() });''',
'''  addMessage(role: string, text: string) {
    // 去重：同一条回复 3 秒内只显示一次
    if (role === 'assistant') {
      const now = Date.now();
      if (text === this.lastAssistant && now - this.lastAssistantTs < 3000) {
        return;
      }
      this.lastAssistant = text;
      this.lastAssistantTs = now;
    }
    this.messages.push({ role: role, text: text, ts: Date.now() });''')
p.write_text(s, encoding="utf-8")
print("app dedupe added")