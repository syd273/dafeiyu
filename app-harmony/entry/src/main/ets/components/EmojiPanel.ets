// 表情面板（独立组件）
import { EmojiItem } from '../common/Config';

const EMOJIS: string[] = [
  '😊', '😄', '😁', '🥰', '😘', '😳',
  '😭', '😤', '🤔', '😴', '😅', '😂',
  '🤣', '😉', '😎', '🥺', '😔', '😡',
  '👍', '👏', '🙏', '❤️', '💔', '🎉',
  '🌙', '⭐', '🐟', '🍜', '☕', '🎵'
];

@Component
export struct EmojiPanel {
  @Prop customEmojis: EmojiItem[] = [];
  onPick: (e: string) => void = () => { };
  onPickImage: (f: string) => void = () => { };

  build() {
    Column() {
      Row() {
        Text('表情').fontSize(12).fontColor('#9db4ef').margin({ left: 14 })
        Blank()
        Text('长按消息可复制/重发/删除').fontSize(11).fontColor('#4a567c').margin({ right: 14 })
      }
      .width('100%').height(30)

      Grid() {
        ForEach(EMOJIS, (e: string) => {
          GridItem() {
            Text(e).fontSize(26).width('100%').height(44).textAlign(TextAlign.Center)
              .onClick(() => { this.onPick(e); })
          }
        }, (e: string) => e)
      }
      .columnsTemplate('1fr 1fr 1fr 1fr 1fr 1fr')
      .rowsGap(2).columnsGap(2)
      .height(220)
      .padding({ left: 10, right: 10, top: 2, bottom: 2 })

      if (this.customEmojis.length > 0) {
        Row() {
          Text('我的表情包').fontSize(11).fontColor('#6f7fae').margin({ left: 14 })
          Blank()
          Text('设置里可添加').fontSize(11).fontColor('#4a567c').margin({ right: 14 })
        }
        .width('100%').margin({ top: 4 })
        Scroll() {
          Row() {
            ForEach(this.customEmojis, (e: EmojiItem) => {
              Image('file://' + e.file)
                .width(54).height(54).borderRadius(8)
                .margin({ left: 8 })
                .border({ width: 1, color: '#2b3350' })
                .onClick(() => { this.onPickImage(e.file); })
            }, (e: EmojiItem) => e.file)
          }
          .padding({ left: 4, right: 8, top: 6, bottom: 8 })
        }
        .scrollable(ScrollDirection.Horizontal)
        .width('100%').height(72)
      }
    }
    .width('100%')
    .backgroundColor('#121826')
  }
}
