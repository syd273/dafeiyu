from pathlib import Path

# 1) MessageList：baseUrl + meme 解析/渲染
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\MessageList.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @Prop herName: string = '安诗鱼';",
              "  @Prop herName: string = '安诗鱼';\n  @Prop baseUrl: string = '';")

# 方法
s = s.replace("""  segments(text: string): string[] {""",
"""  memeId(text: string): string {
    const m = text.match(/\\[meme:\\s*([a-z0-9-]+)\\s*\\]/i);
    return m ? m[1] : '';
  }

  cleanText(text: string): string {
    return text.replace(/\\[meme:\\s*[a-z0-9-]+\\s*\\]/gi, '').trim();
  }

  segments(text: string): string[] {""")

# assistant Flex：cleanText + 表情图片
s = s.replace("""        Flex({ wrap: FlexWrap.Wrap }) {
          ForEach(this.segments(m.text), (seg: string) => {""",
"""        Flex({ wrap: FlexWrap.Wrap }) {
          ForEach(this.segments(this.cleanText(m.text)), (seg: string) => {""")
s = s.replace("""            }
          }, (seg: string) => seg.slice(0, 10) + seg.length)
        }
        .padding({ left: 14, right: 14, top: 9, bottom: 9 })""",
"""            }
          }, (seg: string) => seg.slice(0, 10) + seg.length)
          if (this.memeId(m.text)) {
            Image(`${this.baseUrl}/api/sticker/${this.memeId(m.text)}`)
              .width(110).height(110)
              .objectFit(ImageFit.Contain)
              .borderRadius(8)
              .margin({ top: 6 })
              .onClick(() => { })
          }
        }
        .padding({ left: 14, right: 14, top: 9, bottom: 9 })""")
p.write_text(s, encoding="utf-8")
print("MessageList 表情渲染已加")

# 2) Index 传 baseUrl
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("          herName: this.herName,",
              "          herName: this.herName,\n          baseUrl: this.baseUrl,")
p.write_text(s, encoding="utf-8")
print("Index baseUrl 已传")