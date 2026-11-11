from pathlib import Path

# MessageList：加 herName
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\MessageList.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @Prop theme: string = '#3b6ef5';",
              "  @Prop theme: string = '#3b6ef5';\n  @Prop herName: string = '安诗鱼';")
s = s.replace("      Text('安诗鱼').fontSize(21).fontColor('#cfe0ff').fontWeight(FontWeight.Medium).margin({ top: 14 })",
              "      Text(this.herName).fontSize(21).fontColor('#cfe0ff').fontWeight(FontWeight.Medium).margin({ top: 14 })")
p.write_text(s, encoding="utf-8")
print("MessageList herName ok")

# Index：名字
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State herAvatar: string = '';",
              "  @State herAvatar: string = '';\n  @State herName: string = '安诗鱼';")
s = s.replace("    this.herAvatar = await AppConfig.getAvatar(ctx, 'her');",
              "    this.herAvatar = await AppConfig.getAvatar(ctx, 'her');\n    this.herName = await AppConfig.getName(ctx);")
s = s.replace("""        TopBar({
          name: '安诗鱼',""",
"""        TopBar({
          name: this.herName,""")
s = s.replace("""          myAvatar: this.myAvatar,
          herAvatar: this.herAvatar,
          theme: this.theme,""",
"""          myAvatar: this.myAvatar,
          herAvatar: this.herAvatar,
          theme: this.theme,
          herName: this.herName,""")
p.write_text(s, encoding="utf-8")
print("Index name ok")