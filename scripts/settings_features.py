from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

s = s.replace("  @State keyMsg: string = '';",
              "  @State keyMsg: string = '';\n  @State featRoom: boolean = true;\n  @State featStickers: boolean = true;\n  @State featTrends: boolean = true;")

s = s.replace("    await this.loadApiKey();", "    await this.loadApiKey();\n    await this.loadFeatures();")

s = s.replace("  async loadPersona() {",
"""  async loadFeatures() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/features?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 6000, readTimeout: 6000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.featRoom = (d.room ?? true) as boolean;
        this.featStickers = (d.stickers ?? true) as boolean;
        this.featTrends = (d.trends ?? true) as boolean;
      }
    } catch (e) { }
  }

  async saveFeature(key: string, value: boolean) {
    try {
      const req = http.createHttp();
      const body = `{"${key}": ${value}}`;
      await req.request(`${this.baseUrl2}/api/features?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: body,
        connectTimeout: 6000, readTimeout: 6000,
      });
      req.destroy();
    } catch (e) { }
  }

  async loadPersona() {""")

# UI：功能开关卡片（插在"她的内容来源"卡片后、更多前）
s = s.replace("""          // 更多""",
"""          // 功能开关
          Column() {
            Text('🔌  功能开关').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Column() {
                Text('房间展示').fontSize(13).fontColor('#e8eeff')
                Text('上帝视角的 3D 房间').fontSize(10).fontColor('#5f6c96').margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Start)
              .layoutWeight(1)
              Toggle({ type: ToggleType.Switch, isOn: this.featRoom })
                .selectedColor('#3b6ef5')
                .onChange((v: boolean) => { this.featRoom = v; this.saveFeature('room', v); })
            }
            .width('100%').margin({ top: 10 })
            Row() {
              Column() {
                Text('表情包').fontSize(13).fontColor('#e8eeff')
                Text('她发聊天表情').fontSize(10).fontColor('#5f6c96').margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Start)
              .layoutWeight(1)
              Toggle({ type: ToggleType.Switch, isOn: this.featStickers })
                .selectedColor('#3b6ef5')
                .onChange((v: boolean) => { this.featStickers = v; this.saveFeature('stickers', v); })
            }
            .width('100%').margin({ top: 10 })
            Row() {
              Column() {
                Text('网上冲浪').fontSize(13).fontColor('#e8eeff')
                Text('让她知道最近的热点和梗').fontSize(10).fontColor('#5f6c96').margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Start)
              .layoutWeight(1)
              Toggle({ type: ToggleType.Switch, isOn: this.featTrends })
                .selectedColor('#3b6ef5')
                .onChange((v: boolean) => { this.featTrends = v; this.saveFeature('trends', v); })
            }
            .width('100%').margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 更多""")
p.write_text(s, encoding="utf-8")
print("功能开关卡片已加")