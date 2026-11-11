from pathlib import Path

# ===== 1) Index：演示模式 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

s = s.replace("  @State online: boolean = false;",
              "  @State online: boolean = false;\n  @State demoMode: boolean = false;")

# loadStatus 失败 → detect 失败 → 演示模式
s = s.replace("""      this.detectServer().then((ok: boolean) => {
        if (ok) {
          this.loadStatus();
          this.connectWs();
        }
      });""",
"""      this.detectServer().then((ok: boolean) => {
        if (ok) {
          this.loadStatus();
          this.connectWs();
        } else {
          this.enterDemo();
        }
      });""")

# 演示模式方法
s = s.replace("  /** 当前地址连不上时，扫描热点常见 IP 找服务器 */",
"""  enterDemo() {
    if (this.demoMode) return;
    this.demoMode = true;
    this.messages = [
      { role: 'assistant', text: '（演示模式）嗨，我是安诗鱼。这是给你看的示例：她会记住你说过的话，会自己生活、发说说，也能陪你看记忆星图。', ts: Date.now() - 120000, status: 'ok' },
      { role: 'assistant', text: '真正的她跑在你自己的电脑上。打开设置 → 配置教程，按步骤连上服务器就能见到她啦。', ts: Date.now() - 60000, status: 'ok' },
    ];
  }

  /** 当前地址连不上时，扫描热点常见 IP 找服务器 */""")

# 发送时演示模式提示
s = s.replace("""  async sendText(text: string) {
    if (!text || !text.trim()) return;""",
"""  async sendText(text: string) {
    if (!text || !text.trim()) return;
    if (this.demoMode) {
      this.addMsg('assistant', '（演示模式）现在还没连上你的电脑，去设置里配置服务器后再聊吧。', 'ok');
      return;
    }""")

p.write_text(s, encoding="utf-8")
print("Index 演示模式已加")

# ===== 2) MessageList：AI 生成标识 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\MessageList.ets")
s = p.read_text(encoding="utf-8")
# 在 assistant 气泡的 Flex 之后加小字（找气泡 Column 结束处）
s = s.replace("""        .padding({ left: 14, right: 14, top: 9, bottom: 9 })
        .margin({ top: 2 })""",
"""        .padding({ left: 14, right: 14, top: 9, bottom: 9 })
        .margin({ top: 2 })
        if (m.role === 'assistant') {
          Text('AI 生成')
            .fontSize(9).fontColor('#4a567c')
            .margin({ top: 2, left: 4 })
        }""")
p.write_text(s, encoding="utf-8")
print("AI 标识已加")