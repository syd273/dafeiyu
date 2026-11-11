// 打字动画（独立组件的独立状态，只刷新自己）
@Component
export struct TypingDots {
  @State phase: number = 0;
  private timer: number = -1;

  aboutToAppear() {
    this.timer = setInterval(() => {
      this.phase = (this.phase + 1) % 3;
    }, 320);
  }

  aboutToDisappear() {
    if (this.timer >= 0) {
      clearInterval(this.timer);
      this.timer = -1;
    }
  }

  build() {
    Row() {
      ForEach([0, 1, 2], (i: number) => {
        Circle({ width: 6, height: 6 })
          .fill('#7f97d8')
          .margin({ left: 3, right: 3 })
          .opacity(this.phase === i ? 1 : 0.3)
          .translate({ y: this.phase === i ? -3 : 0 })
      }, (i: number) => '' + i)
    }
    .padding({ left: 12, right: 12, top: 13, bottom: 13 })
    .backgroundColor('#1e2434')
    .borderWidth(0.5)
    .borderColor('#2a3350')
    .borderRadius({ topLeft: 6, topRight: 18, bottomLeft: 18, bottomRight: 18 })
    .margin({ left: 8 })
  }
}
