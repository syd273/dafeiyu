// 顶部栏（独立组件，只随状态变化刷新）
@Component
export struct TopBar {
  @Prop name: string = '安诗鱼';
  @Prop online: boolean = false;
  @Prop mood: string = '平静';
  @Prop life: string = '';
  onBack: () => void = () => { };
  onSettings: () => void = () => { };
  onStar: () => void = () => { };
  onSays: () => void = () => { };
  onRefresh: () => void = () => { };

  build() {
    Row() {
      Text('‹')
        .fontSize(28).fontColor('#bcd0ff')
        .width(36).height(36).textAlign(TextAlign.Center)
        .backgroundColor('#1a2138').borderRadius(12)
        .margin({ right: 4 })
        .onClick(() => { this.onBack(); })
      Column() {
        Text(this.name).fontSize(18).fontWeight(FontWeight.Bold).fontColor('#eef2ff')
        Row() {
          Circle({ width: 6, height: 6 }).fill(this.online ? '#4ade80' : '#64748b')
          Text(this.online ? '在线' : '离线')
            .fontSize(11).fontColor(this.online ? '#7fd8a0' : '#8a8fa8').margin({ left: 4 })
          Text(`${this.mood}${this.life ? ' · ' + this.life : ''}`)
            .fontSize(11).fontColor('#66739d').margin({ left: 8 })
            .maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis }).layoutWeight(1)
        }
        .margin({ top: 2 })
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1)
      Text(this.online ? '' : '重连')
        .fontSize(12).fontColor('#ffd48a')
        .padding({ left: 8, right: 8 })
        .onClick(() => { this.onRefresh(); })
      Text('💬')
        .fontSize(15)
        .padding({ left: 8, right: 8 })
        .onClick(() => { this.onSays(); })
      Text('⭐')
        .fontSize(16).fontColor('#bcd0ff')
        .width(36).height(36).textAlign(TextAlign.Center)
        .backgroundColor('#1a2138').borderRadius(12)
        .margin({ right: 8 })
        .onClick(() => { this.onStar(); })
      Text('⚙')
        .fontSize(18).fontColor('#bcd0ff')
        .width(36).height(36).textAlign(TextAlign.Center)
        .backgroundColor('#1a2138').borderRadius(12)
        .onClick(() => { this.onSettings(); })
    }
    .width('100%')
    .height(58)
    .padding({ left: 8, right: 14 })
    .backgroundColor('#11151f')
  }
}
