from pathlib import Path

# TopBar 加星图按钮
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\TopBar.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  onBack: () => void = () => { };\n  onSettings: () => void = () => { };",
"""  onBack: () => void = () => { };
  onSettings: () => void = () => { };
  onStar: () => void = () => { };""")
s = s.replace("""      Text('⚙')
        .fontSize(18).fontColor('#bcd0ff')
        .width(36).height(36).textAlign(TextAlign.Center)
        .backgroundColor('#1a2138').borderRadius(12)
        .onClick(() => { this.onSettings(); })""",
"""      Text('⭐')
        .fontSize(16).fontColor('#bcd0ff')
        .width(36).height(36).textAlign(TextAlign.Center)
        .backgroundColor('#1a2138').borderRadius(12)
        .margin({ right: 8 })
        .onClick(() => { this.onStar(); })
      Text('⚙')
        .fontSize(18).fontColor('#bcd0ff')
        .width(36).height(36).textAlign(TextAlign.Center)
        .backgroundColor('#1a2138').borderRadius(12)
        .onClick(() => { this.onSettings(); })""")
p.write_text(s, encoding="utf-8")
print("TopBar 星图按钮已加")

# Index 传 onStar
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""          onBack: () => { router.back(); },
          onSettings: () => { router.pushUrl({ url: 'pages/Settings' }); },""",
"""          onBack: () => { router.back(); },
          onSettings: () => { router.pushUrl({ url: 'pages/Settings' }); },
          onStar: () => { router.pushUrl({ url: 'pages/StarMap' }); },""")
p.write_text(s, encoding="utf-8")
print("Index 星图入口已加")