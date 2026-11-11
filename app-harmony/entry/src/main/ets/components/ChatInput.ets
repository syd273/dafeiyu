// 输入栏（独立组件：输入文字只刷新自己）
@Component
export struct ChatInput {
  @Link sending: boolean;
  @Prop @Watch('onDraftChanged') draft: string = '';
  // 底部导航条高度（EntryAbility 写入），输入栏必须避让，否则被手势条压住
  @StorageProp('navBarHeight') navH: number = 28;
  @State text: string = '';
  onSend: (t: string) => void = () => { };
  onToggleEmoji: () => void = () => { };
  onPickImage: () => void = () => { };
  onFocusInput: () => void = () => { };

  onDraftChanged() {
    if (this.draft) {
      this.text = this.draft;
    }
  }

  send() {
    const t = this.text.trim();
    if (!t || this.sending) return;
    this.text = '';
    this.onSend(t);
  }

  build() {
    Row() {
      Text('＋')
        .fontSize(20).width(36).height(36).textAlign(TextAlign.Center)
        .fontColor('#bcd0ff').backgroundColor('#161b29').borderRadius(18)
        .onClick(() => { this.onPickImage(); })
      Text('😊')
        .fontSize(23).width(40).height(40).textAlign(TextAlign.Center)
        .backgroundColor('#161b29').borderRadius(20)
        .margin({ left: 6 })
        .onClick(() => { this.onToggleEmoji(); })

      TextArea({ text: this.text, placeholder: '发消息…' })
        .layoutWeight(1)
        .constraintSize({ minHeight: 40, maxHeight: 96 })
        .maxLines(4)
        .fontSize(15).fontColor('#e8eeff').placeholderColor('#5f6c96')
        .backgroundColor('#161b29').borderRadius(20)
        .border({ width: 0.5, color: '#232d47' })
        .padding({ left: 15, right: 15, top: 9, bottom: 9 })
        .margin({ left: 8 })
        .onChange((v: string) => { this.text = v; })
        .onFocus(() => { this.onFocusInput(); })
        .onSubmit(() => { this.send(); })

      Button(this.sending ? '…' : '↑')
        .height(42).width(42).margin({ left: 8 })
        .fontSize(this.sending ? 16 : 20)
        .fontWeight(FontWeight.Medium)
        .fontColor(this.text.trim().length > 0 ? '#ffffff' : '#5f6c96')
        .backgroundColor(this.text.trim().length > 0 ? '#3b6ef5' : '#1a2138')
        .borderRadius(21)
        .enabled(!this.sending && this.text.trim().length > 0)
        .onClick(() => { this.send(); })
    }
    .width('100%')
    .padding({ left: 12, right: 12, top: 8, bottom: 12 + this.navH })
    .backgroundColor('#11151f')
    .alignItems(VerticalAlign.Bottom)
  }
}
