from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# 1) 状态
s = s.replace("  @State baseUrl: string = DEFAULT_BASE;",
"""  @State baseUrl: string = DEFAULT_BASE;
  @State theme: string = '#3b6ef5';
  @State bgKey: string = 'default';
  @State bgImage: string = '';""")

# 2) 读取配置
s = s.replace("    this.customEmojis = await AppConfig.getEmojis(ctx);",
"""    this.customEmojis = await AppConfig.getEmojis(ctx);
    this.theme = await AppConfig.getTheme(ctx);
    this.bgKey = await AppConfig.getBg(ctx);
    this.bgImage = await AppConfig.getBgImage(ctx);""")

# 3) 背景色辅助方法（插到 wsUrl 前）
s = s.replace("  wsUrl(): string {",
"""  bgFrom(): string {
    if (this.bgKey === 'night') return '#0b1020';
    if (this.bgKey === 'gray') return '#101114';
    if (this.bgKey === 'warm') return '#171310';
    return '#0d1017';
  }

  bgTo(): string {
    if (this.bgKey === 'night') return '#131a2e';
    if (this.bgKey === 'gray') return '#16181d';
    if (this.bgKey === 'warm') return '#211812';
    return '#0d1017';
  }

  wsUrl(): string {""")

# 4) 消息区背景层
s = s.replace("""      Stack() {
        if (this.messages.length === 0) {
          this.emptyState()
        }""",
"""      Stack() {
        if (this.bgKey === 'custom' && this.bgImage) {
          Image('file://' + this.bgImage)
            .width('100%').height('100%').objectFit(ImageFit.Cover).opacity(0.9)
        } else {
          Column()
            .width('100%').height('100%')
            .linearGradient({ angle: 160, colors: [[this.bgFrom(), 0], [this.bgTo(), 1]] })
        }
        if (this.messages.length === 0) {
          this.emptyState()
        }""")

# 5) 主题色应用到气泡与发送按钮
s = s.replace(".backgroundColor('#3b6ef5')", ".backgroundColor(this.theme)")
s = s.replace(".backgroundColor(this.input.trim().length > 0 ? '#3b6ef5' : '#1a2138')",
              ".backgroundColor(this.input.trim().length > 0 ? this.theme : '#1a2138')")

# 6) 顶部按钮更精致
s = s.replace("""        Text('‹')
          .fontSize(30).fontColor('#9db4ef').fontWeight(FontWeight.Lighter)
          .width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })""",
"""        Text('‹')
          .fontSize(28).fontColor('#bcd0ff')
          .width(36).height(36).textAlign(TextAlign.Center)
          .backgroundColor('#1a2138').borderRadius(12)
          .margin({ right: 4 })
          .onClick(() => { router.back(); })""")
s = s.replace("""        Text('⚙').fontSize(19).fontColor('#9db4ef').padding({ left: 8, right: 4 })
          .onClick(() => { router.pushUrl({ url: 'pages/Settings' }); })""",
"""        Text('⚙')
          .fontSize(18).fontColor('#bcd0ff')
          .width(36).height(36).textAlign(TextAlign.Center)
          .backgroundColor('#1a2138').borderRadius(12)
          .onClick(() => { router.pushUrl({ url: 'pages/Settings' }); })""")

p.write_text(s, encoding="utf-8")
print("Index theme applied")