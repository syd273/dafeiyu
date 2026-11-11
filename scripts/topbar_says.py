from pathlib import Path

# TopBar：加说说按钮
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\TopBar.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  onStar: () => void = () => { };",
              "  onStar: () => void = () => { };\n  onSays: () => void = () => { };")
s = s.replace("""      Text('⭐')""",
"""      Text('💬')
        .fontSize(15)
        .padding({ left: 8, right: 8 })
        .onClick(() => { this.onSays(); })
      Text('⭐')""")
p.write_text(s, encoding="utf-8")
print("TopBar 说说按钮已加")

# Index：传 onSays
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("          onStar: () => { router.pushUrl({ url: 'pages/StarMap' }); },",
"""          onStar: () => { router.pushUrl({ url: 'pages/StarMap' }); },
          onSays: () => { router.pushUrl({ url: 'pages/Says' }); },""")
p.write_text(s, encoding="utf-8")
print("Index 已接入")