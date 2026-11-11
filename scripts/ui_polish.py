from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# 1) 头像改圆形
s = s.replace("""      Image('file://' + path)
        .width(size).height(size).borderRadius(size * 0.28)
        .border({ width: 1, color: '#2b3350' })
    } else if (fallback) {
      Image($r('app.media.anshiyu_avatar'))
        .width(size).height(size).borderRadius(size * 0.28)
        .border({ width: 1, color: '#2b3350' })
    } else {
      Text('东')
        .width(size).height(size).fontSize(size * 0.34).fontColor('#cfe0ff')
        .textAlign(TextAlign.Center).backgroundColor('#25324f').borderRadius(size * 0.28)
    }""",
"""      Image('file://' + path)
        .width(size).height(size).borderRadius(size / 2)
        .border({ width: 1, color: '#2b3350' })
    } else if (fallback) {
      Image($r('app.media.anshiyu_avatar'))
        .width(size).height(size).borderRadius(size / 2)
        .border({ width: 1, color: '#2b3350' })
    } else {
      Text('东')
        .width(size).height(size).fontSize(size * 0.34).fontColor('#cfe0ff')
        .textAlign(TextAlign.Center).backgroundColor('#25324f').borderRadius(size / 2)
    }""")

# 2) 气泡加阴影 + 入场过渡
s = s.replace("""          Text(m.text)
            .fontSize(16).lineHeight(23).fontColor('#ffffff')
            .padding({ left: 14, right: 14, top: 9, bottom: 9 })
            .backgroundColor(this.theme)
            .borderRadius({ topLeft: 18, topRight: 18, bottomLeft: 18, bottomRight: 6 })
            .constraintSize({ maxWidth: '72%' })""",
"""          Text(m.text)
            .fontSize(16).lineHeight(23).fontColor('#ffffff')
            .padding({ left: 14, right: 14, top: 9, bottom: 9 })
            .backgroundColor(this.theme)
            .borderRadius({ topLeft: 18, topRight: 18, bottomLeft: 18, bottomRight: 6 })
            .constraintSize({ maxWidth: '72%' })
            .shadow({ radius: 8, color: '#40000000', offsetY: 2 })""")
s = s.replace("""        Text(m.text)
          .fontSize(16).lineHeight(23).fontColor('#e8eeff')
          .padding({ left: 14, right: 14, top: 9, bottom: 9 })
          .backgroundColor('#1e2434')
          .border({ width: 0.5, color: '#2a3350' })
          .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
          .constraintSize({ maxWidth: '72%' })
          .margin({ left: 8 })""",
"""        Text(m.text)
          .fontSize(16).lineHeight(23).fontColor('#e8eeff')
          .padding({ left: 14, right: 14, top: 9, bottom: 9 })
          .backgroundColor('#1e2434')
          .border({ width: 0.5, color: '#2a3350' })
          .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
          .constraintSize({ maxWidth: '72%' })
          .margin({ left: 8 })
          .shadow({ radius: 8, color: '#33000000', offsetY: 2 })""")

# 3) ListItem 入场过渡
s = s.replace("""          ForEach(this.messages, (m: ChatMsg, idx: number) => {
            ListItem() {
              Column() {
                if (this.showTime(idx)) {
                  this.timeDivider(m.ts)
                }
                this.bubble(m)
              }
            }
          }, (m: ChatMsg) => `${m.ts}_${m.role}_${m.text.slice(0, 10)}`)""",
"""          ForEach(this.messages, (m: ChatMsg, idx: number) => {
            ListItem() {
              Column() {
                if (this.showTime(idx)) {
                  this.timeDivider(m.ts)
                }
                this.bubble(m)
              }
            }
            .transition(TransitionEffect.OPACITY.combine(TransitionEffect.translate({ y: 10 })))
          }, (m: ChatMsg) => `${m.ts}_${m.role}_${m.text.slice(0, 10)}`)""")

# 4) 顶部栏：名字加粗、底部细线、状态点
s = s.replace("""          Text('安诗鱼').fontSize(17).fontWeight(FontWeight.Medium).fontColor('#eef2ff')""",
"""          Text('安诗鱼').fontSize(18).fontWeight(FontWeight.Bold).fontColor('#eef2ff')""")

# 5) 发送按钮主题色渐变 + 按压态
s = s.replace("""        Button(this.sending ? '…' : '↑')
          .height(40).width(40).margin({ left: 8 })
          .fontSize(this.sending ? 16 : 20)
          .fontWeight(FontWeight.Medium)
          .fontColor(this.input.trim().length > 0 ? '#ffffff' : '#5f6c96')
          .backgroundColor(this.input.trim().length > 0 ? this.theme : '#1a2138')
          .borderRadius(20)
          .enabled(!this.sending && this.input.trim().length > 0)
          .onClick(() => { this.send(); })""",
"""        Button(this.sending ? '…' : '↑')
          .height(42).width(42).margin({ left: 8 })
          .fontSize(this.sending ? 16 : 20)
          .fontWeight(FontWeight.Medium)
          .fontColor(this.input.trim().length > 0 ? '#ffffff' : '#5f6c96')
          .linearGradient({
            angle: 135,
            colors: this.input.trim().length > 0
              ? [[this.theme, 0], [this.theme + 'c0', 1]]
              : [['#1a2138', 0], ['#1a2138', 1]]
          })
          .borderRadius(21)
          .enabled(!this.sending && this.input.trim().length > 0)
          .onClick(() => { this.send(); })
          .onTouch((event: TouchEvent) => {
            if (event.type === TouchType.Down) this.sendPressed = true;
            if (event.type === TouchType.Up || event.type === TouchType.Cancel) this.sendPressed = false;
          })
          .scale({ x: this.sendPressed ? 0.92 : 1, y: this.sendPressed ? 0.92 : 1 })
          .animation({ duration: 120, curve: Curve.EaseOut })""")

# 6) 状态变量
s = s.replace("  @State titleOffset: number = 14;",
              "  @State titleOffset: number = 14;\n  @State sendPressed: boolean = false;")

p.write_text(s, encoding="utf-8")
print("Index visual upgraded")