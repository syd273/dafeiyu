from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Legacy.ets")
s = p.read_text(encoding="utf-8")

# 删除 trigger 方法
start = s.find("  async trigger() {")
if start >= 0:
    end = s.find("  fmt(ts: number)", start)
    if end >= 0:
        s = s[:start] + s[end:]

# 删除按钮与提示 UI，换说明
s = s.replace("""          // 手动传承
          Button(this.loading ? '传承中…' : '让她现在就传承')
            .height(40).width('100%').margin({ top: 12 })
            .backgroundColor('#3a2530').fontSize(13).fontColor('#ffb4b4')
            .borderRadius(12)
            .enabled(!this.loading)
            .onClick(() => { this.trigger(); })

          if (this.tip) {
            Text(this.tip).fontSize(11).fontColor('#ffd48a').margin({ top: 8 }).width('100%')
          }""",
"""          Text('传承不能手动触发。等这一生的字数满了，她会自己写下总结、交给下一代。')
            .fontSize(12).lineHeight(19).fontColor('#7f8db5')
            .width('100%').padding(14)
            .backgroundColor('#161b29')
            .borderRadius(12)
            .margin({ top: 12 })""")
p.write_text(s, encoding="utf-8")
print("手动传承已移除")