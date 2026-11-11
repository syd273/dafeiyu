# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\MessageList.ets")
s = p.read_text(encoding="utf-8")

old = """        Flex({ wrap: FlexWrap.Wrap }) {
          ForEach(this.segments(this.cleanText(m.text)), (seg: string) => {
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
          if (this.memeId(m.text)) {
            Image(`${this.baseUrl}/api/sticker/${this.memeId(m.text)}`)
              .width(110).height(110)
              .objectFit(ImageFit.Contain)
              .borderRadius(8)
              .margin({ top: 6 })
              .onClick(() => { })
          }
        }
        .padding({ left: 14, right: 14, top: 9, bottom: 9 })
        .backgroundColor('#1e2434')
        .border({ width: 0.5, color: '#2a3350' })
        .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
        .constraintSize({ maxWidth: '72%' })
        .margin({ left: 8 })
        .bindContextMenu(this.msgMenu(m, idx), ResponseType.LongPress)
        Blank()"""

new = """        Column() {
          Flex({ wrap: FlexWrap.Wrap }) {
            ForEach(this.segments(this.cleanText(m.text)), (seg: string) => {
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
            if (this.memeId(m.text)) {
              Image(`${this.baseUrl}/api/sticker/${this.memeId(m.text)}`)
                .width(110).height(110)
                .objectFit(ImageFit.Contain)
                .borderRadius(8)
                .margin({ top: 6 })
                .onClick(() => { })
            }
          }
          .padding({ left: 14, right: 14, top: 9, bottom: 9 })
          .backgroundColor('#1e2434')
          .border({ width: 0.5, color: '#2a3350' })
          .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
          .constraintSize({ maxWidth: '72%' })
          .margin({ left: 8 })
          .bindContextMenu(this.msgMenu(m, idx), ResponseType.LongPress)
          Text('AI 生成').fontSize(9).fontColor('#4a567c').margin({ left: 10, top: 2 })
        }
        .alignItems(HorizontalAlign.Start)
        Blank()"""

if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("AI 标识已插入")
else:
    print("未匹配到 assistant 气泡块")
