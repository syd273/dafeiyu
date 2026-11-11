from pathlib import Path

# 1) MessageList：链接拆段渲染 + 回调
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\MessageList.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  onRetry: (i: number) => void = () => { };",
"""  onRetry: (i: number) => void = () => { };
  onOpenLink: (url: string) => void = () => { };""")

# 拆段方法
s = s.replace("""  copyText(text: string) {""",
"""  segments(text: string): string[] {
    const out: string[] = [];
    const re = /https?:\\/\\/[^\\s，。]+/g;
    let last = 0;
    let m: RegExpExecArray | null = re.exec(text);
    while (m !== null) {
      if (m.index > last) out.push(text.substring(last, m.index));
      out.push(m[0]);
      last = m.index + m[0].length;
      m = re.exec(text);
    }
    if (last < text.length) out.push(text.substring(last));
    return out.length > 0 ? out : [text];
  }

  copyText(text: string) {""")

# 气泡：她的消息用 Flex 分段渲染
s = s.replace("""        Text(m.text)
          .fontSize(16).lineHeight(23).fontColor('#e8eeff')
          .padding({ left: 14, right: 14, top: 9, bottom: 9 })
          .backgroundColor('#1e2434')
          .border({ width: 0.5, color: '#2a3350' })
          .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
          .constraintSize({ maxWidth: '72%' })
          .margin({ left: 8 })
          .bindContextMenu(this.msgMenu(m, idx), ResponseType.LongPress)""",
"""        Flex({ wrap: FlexWrap.Wrap }) {
          ForEach(this.segments(m.text), (seg: string) => {
            if (seg.startsWith('http')) {
              Text(seg)
                .fontSize(15).lineHeight(23).fontColor('#8fb8ff')
                .decoration({ type: TextDecorationType.Underline, color: '#8fb8ff' })
                .constraintSize({ maxWidth: '100%' })
                .onClick(() => { this.onOpenLink(seg); })
            } else {
              Text(seg)
                .fontSize(16).lineHeight(23).fontColor('#e8eeff')
                .constraintSize({ maxWidth: '100%' })
            }
          }, (seg: string) => seg.slice(0, 10) + seg.length)
        }
        .padding({ left: 14, right: 14, top: 9, bottom: 9 })
        .backgroundColor('#1e2434')
        .border({ width: 0.5, color: '#2a3350' })
        .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
        .constraintSize({ maxWidth: '72%' })
        .margin({ left: 8 })
        .bindContextMenu(this.msgMenu(m, idx), ResponseType.LongPress)""")
p.write_text(s, encoding="utf-8")
print("MessageList 链接渲染已加")

# 2) Index：openUrl
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""  /** 失败重试 */""",
"""  /** 打开链接：优先调起手机里的 B站/抖音 App，失败回退浏览器 */
  async openUrl(url: string) {
    const ctx = getContext(this) as common.UIAbilityContext;
    let uri = url;
    try {
      const m = url.match(/bilibili\\.com\\/video\\/(BV[0-9A-Za-z]+)/);
      if (m) {
        uri = `bilibili://video/${m[1]}`;
      } else if (url.indexOf('douyin.com') >= 0) {
        uri = `snssdk1128://webview?url=${encodeURIComponent(url)}`;
      }
      await ctx.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        entities: ['entity.system.browsable'],
      });
    } catch (e) {
      try {
        await ctx.startAbility({
          action: 'ohos.want.action.viewData',
          uri: url,
          entities: ['entity.system.browsable'],
        });
      } catch (e2) { }
    }
  }

  /** 失败重试 */""")
s = s.replace("""          onRetry: (i: number) => { this.retrySend(i); },""",
"""          onRetry: (i: number) => { this.retrySend(i); },
          onOpenLink: (url: string) => { this.openUrl(url); },""")
p.write_text(s, encoding="utf-8")
print("Index openUrl 已加")