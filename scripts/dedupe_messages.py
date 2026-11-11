from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# addMsg 带 ts + 强去重
s = s.replace("""  addMsg(role: string, text: string, status: string = 'ok') {
    if (role === 'assistant') {
      const now = Date.now();
      if (text === this.lastAssistant && now - this.lastAssistantTs < 3000) return;
      this.lastAssistant = text;
      this.lastAssistantTs = now;
    }
    this.messages = this.messages.concat([{ role: role, text: text, ts: Date.now(), status: status }]);
    this.saveHistory();
  }""",
"""  addMsg(role: string, text: string, status: string = 'ok', ts: number = 0) {
    const msgTs = ts > 0 ? ts : Date.now();
    // 去重：同一条消息（补收 + 实时广播）只保留一条
    const recent = this.messages.slice(-30);
    for (const m of recent) {
      if (m.role === role && m.text === text && Math.abs(m.ts - msgTs) < 120000) {
        return;
      }
    }
    if (role === 'assistant') {
      if (text === this.lastAssistant && msgTs - this.lastAssistantTs < 3000) return;
      this.lastAssistant = text;
      this.lastAssistantTs = msgTs;
    }
    this.messages = this.messages.concat([{ role: role, text: text, ts: msgTs, status: status }]);
    this.saveHistory();
  }""")

# syncRecent 传源 ts
s = s.replace("""          const text = (it.text ?? '') as string;
          if (!text) continue;
          this.addMsg('assistant', text);""",
"""          const text = (it.text ?? '') as string;
          if (!text) continue;
          const its = ((it.ts ?? 0) as number) * 1000;
          this.addMsg('assistant', text, 'ok', its);""")

# WS 传源 ts
s = s.replace("""          if (m.type === 'message' && m.role === 'assistant' && m.text) {
            this.addMsg('assistant', m.text);""",
"""          if (m.type === 'message' && m.role === 'assistant' && m.text) {
            const wts = m.ts ? Number(m.ts) * 1000 : 0;
            this.addMsg('assistant', m.text, 'ok', wts);""")
p.write_text(s, encoding="utf-8")
print("去重已加")