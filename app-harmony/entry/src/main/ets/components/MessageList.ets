// 消息列表（独立组件：新消息才重建，滚动/动画在组件内）
import { pasteboard } from '@kit.BasicServicesKit';
import { TypingDots } from './TypingDots';

export interface ChatMsg {
  role: string;   // user / assistant
  text: string;
  ts: number;
  status?: string;  // sending / ok / failed
}

interface MsgGroup {
  dateKey: string;
  dateLabel: string;
  items: ChatMsg[];
}

@Component
export struct MessageList {
  @Prop @Watch('onMessages') messages: ChatMsg[] = [];
  @Prop sending: boolean = false;
  @Prop bgKey: string = 'default';
  @Prop bgFrom: string = '#0d1017';
  @Prop bgTo: string = '#0d1017';
  @Prop bgImage: string = '';
  @Prop myAvatar: string = '';
  @Prop herAvatar: string = '';
  @Prop theme: string = '#3b6ef5';
  @Prop herName: string = '安诗鱼';
  @Prop baseUrl: string = '';
  onQuick: (t: string) => void = () => { };
  onResend: (t: string) => void = () => { };
  onDelete: (i: number) => void = () => { };
  onRetry: (i: number) => void = () => { };
  onOpenLink: (url: string) => void = () => { };

  @State groupList: MsgGroup[] = [];
  private scroller: Scroller = new Scroller();

  aboutToAppear() {
    this.rebuild();
  }

  onMessages() {
    this.rebuild();
    this.scrollBottom();
  }

  rebuild() {
    const out: MsgGroup[] = [];
    for (const m of this.messages) {
      const key = this.dateKey(m.ts);
      if (out.length === 0 || out[out.length - 1].dateKey !== key) {
        out.push({ dateKey: key, dateLabel: this.dateLabel(m.ts), items: [] });
      }
      out[out.length - 1].items.push(m);
    }
    this.groupList = out;
  }

  scrollBottom() {
    setTimeout(() => { try { this.scroller.scrollEdge(Edge.Bottom); } catch (e) { } }, 80);
    setTimeout(() => { try { this.scroller.scrollEdge(Edge.Bottom); } catch (e) { } }, 300);
  }

  dateLabel(ts: number): string {
    const d = new Date(ts);
    const now = new Date();
    if (d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate()) {
      return '今天';
    }
    const y = new Date(now.getTime() - 86400000);
    if (d.getFullYear() === y.getFullYear() && d.getMonth() === y.getMonth() && d.getDate() === y.getDate()) {
      return '昨天';
    }
    return `${d.getMonth() + 1}月${d.getDate()}日`;
  }

  dateKey(ts: number): string {
    const d = new Date(ts);
    return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
  }

  showTime(index: number, items: ChatMsg[]): boolean {
    if (index === 0) return false;
    return items[index].ts - items[index - 1].ts > 5 * 60 * 1000;
  }

  timeLabel(ts: number): string {
    const d = new Date(ts);
    const p = (n: number): string => n < 10 ? '0' + n : '' + n;
    return `${p(d.getHours())}:${p(d.getMinutes())}`;
  }

  memeId(text: string): string {
    const m = text.match(/\[meme:\s*([a-z0-9-]+)\s*\]/i);
    return m ? m[1] : '';
  }

  cleanText(text: string): string {
    return text.replace(/\[meme:\s*[a-z0-9-]+\s*\]/gi, '').trim();
  }

  segments(text: string): string[] {
    const out: string[] = [];
    const re = /https?:\/\/[^\s，。]+/g;
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

  copyText(text: string) {
    try {
      const data = pasteboard.createData(pasteboard.MIMETYPE_TEXT_PLAIN, text);
      pasteboard.getSystemPasteboard().setData(data);
    } catch (e) { }
  }

  @Builder
  avatarView(path: string, size: number, fallback: string) {
    if (path) {
      Image('file://' + path)
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
    }
  }

  @Builder
  timeDivider(ts: number) {
    Row() {
      Text(this.timeLabel(ts))
        .fontSize(11).fontColor('#5d6a92')
        .padding({ left: 10, right: 10, top: 3, bottom: 3 })
        .backgroundColor('#141a28').borderRadius(9)
    }
    .width('100%').justifyContent(FlexAlign.Center).padding({ top: 8, bottom: 4 })
  }

  @Builder
  dateHeader(label: string) {
    Row() {
      Text(label)
        .fontSize(11).fontColor('#8fa2d8')
        .padding({ left: 12, right: 12, top: 4, bottom: 4 })
        .backgroundColor('#141a28')
        .borderRadius(10)
    }
    .width('100%').justifyContent(FlexAlign.Center).padding({ top: 10, bottom: 6 })
  }

  @Builder
  msgMenu(m: ChatMsg, idx: number) {
    Menu() {
      MenuItem({ content: '复制' }).onClick(() => { this.copyText(m.text); })
      MenuItem({ content: '重发' }).onClick(() => { this.onResend(m.text); })
      MenuItem({ content: '删除' }).onClick(() => { this.onDelete(idx); })
    }
  }

  @Builder
  bubble(m: ChatMsg, idx: number) {
    Row() {
      if (m.role === 'user') {
        Blank()
        if (m.text.startsWith('[img:')) {
          Image('file://' + m.text.substring(5, m.text.length - 1))
            .width(104).height(104).borderRadius(12).objectFit(ImageFit.Cover)
            .bindContextMenu(this.msgMenu(m, idx), ResponseType.LongPress)
        } else {
          Text(m.text)
            .fontSize(16).lineHeight(23).fontColor('#ffffff')
            .padding({ left: 14, right: 14, top: 9, bottom: 9 })
            .backgroundColor(this.theme)
            .borderRadius({ topLeft: 18, topRight: 18, bottomLeft: 18, bottomRight: 6 })
            .constraintSize({ maxWidth: '72%' })
            .bindContextMenu(this.msgMenu(m, idx), ResponseType.LongPress)
        }
        Column() {
          if (this.myAvatar) {
            Image('file://' + this.myAvatar)
              .width(32).height(32).borderRadius(16)
          } else {
            Text('东')
              .width(32).height(32).fontSize(12).fontColor('#cfe0ff')
              .textAlign(TextAlign.Center).backgroundColor('#25324f').borderRadius(16)
          }
          if (m.status === 'sending') {
            Text('发送中').fontSize(9).fontColor('#8fa2d8').margin({ top: 2 })
          } else if (m.status === 'failed') {
            Text('失败·重试').fontSize(9).fontColor('#ff6b6b').margin({ top: 2 })
              .onClick(() => { this.onRetry(idx); })
          }
        }
        .alignItems(HorizontalAlign.Center)
        .margin({ left: 8, top: 2 })
      } else {
        this.avatarView(this.herAvatar, 32, 'her')
        Column() {
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
        Blank()
      }
    }
    .width('100%')
    .alignItems(VerticalAlign.Top)
    .padding({ top: 2, bottom: 2 })
  }

  @Builder
  emptyState() {
    Column() {
      this.avatarView(this.herAvatar, 88, 'her')
      Text(this.herName).fontSize(21).fontColor('#cfe0ff').fontWeight(FontWeight.Medium).margin({ top: 14 })
      Text('她有自己的生活，也会想你').fontSize(13).fontColor('#66739d').margin({ top: 8 })
      Row() {
        Text('在吗')
          .fontSize(13).fontColor('#9db4ef')
          .padding({ left: 14, right: 14, top: 7, bottom: 7 })
          .backgroundColor('#161d2e')
          .border({ width: 0.5, color: '#2a3350' })
          .borderRadius(16)
          .onClick(() => { this.onQuick('在吗'); })
        Text('今天过得怎么样')
          .fontSize(13).fontColor('#9db4ef')
          .padding({ left: 14, right: 14, top: 7, bottom: 7 })
          .backgroundColor('#161d2e')
          .border({ width: 0.5, color: '#2a3350' })
          .borderRadius(16)
          .margin({ left: 10 })
          .onClick(() => { this.onQuick('今天过得怎么样？'); })
      }
      .margin({ top: 18 })
      Text('右上角 ⚙ 可换头像、加表情包').fontSize(11).fontColor('#3f4a6b').margin({ top: 18 })
    }
    .width('100%').height('100%').justifyContent(FlexAlign.Center)
  }

  build() {
    Stack() {
      if (this.bgKey === 'custom' && this.bgImage) {
        Image('file://' + this.bgImage)
          .width('100%').height('100%').objectFit(ImageFit.Cover).opacity(0.9)
      } else {
        Column()
          .width('100%').height('100%')
          .linearGradient({ angle: 160, colors: [[this.bgFrom, 0], [this.bgTo, 1]] })
      }

      List({ scroller: this.scroller }) {
        ForEach(this.groupList, (g: MsgGroup) => {
          ListItemGroup({ header: this.dateHeader(g.dateLabel), space: 2 }) {
            ForEach(g.items, (m: ChatMsg, i: number) => {
              ListItem() {
                Column() {
                  if (this.showTime(i, g.items)) {
                    this.timeDivider(m.ts)
                  }
                  this.bubble(m, this.messages.indexOf(m))
                }
              }
            }, (m: ChatMsg) => `${m.ts}_${m.role}_${m.text.slice(0, 10)}`)
          }
        }, (g: MsgGroup) => `${g.dateKey}_${g.items.length}_${g.items[g.items.length - 1].ts}`)

        if (this.sending) {
          ListItem() {
            Row() {
              this.avatarView(this.herAvatar, 32, 'her')
              TypingDots()
              Blank()
            }
            .width('100%')
            .alignItems(VerticalAlign.Top)
            .padding({ top: 2, bottom: 2 })
          }
        }
      }
      .width('100%').height('100%')
      .padding({ left: 12, right: 12, top: 4, bottom: 10 })
      .scrollBar(BarState.Off)
      .edgeEffect(EdgeEffect.Spring)
      .sticky(StickyStyle.Header)

      if (this.messages.length === 0) {
        this.emptyState()
      }
    }
    .width('100%').height('100%')
  }
}
