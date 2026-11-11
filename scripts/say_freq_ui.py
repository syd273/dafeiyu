from pathlib import Path

# 1) Says.ets：移除按钮与 say 方法
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Says.ets")
s = p.read_text(encoding="utf-8")
start = s.find("  async say() {")
if start >= 0:
    end = s.find("  fmt(ts: number)", start)
    if end >= 0:
        s = s[:start] + s[end:]
s = s.replace("""          Button(this.loading ? '她说…' : '让她发一条说说')
            .height(40).width('100%').margin({ top: 12 })
            .backgroundColor('#3b6ef5').fontSize(14).fontColor('#ffffff')
            .borderRadius(20)
            .enabled(!this.loading)
            .onClick(() => { this.say(); })
""",
"""          Text('她会自己发说说，你可以在设置里调她的说说频率')
            .fontSize(11).fontColor('#5f6c96').width('100%').margin({ top: 10 })
""")
p.write_text(s, encoding="utf-8")
print("说说按钮已移除")

# 2) Settings：加说说频率
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State backupFiles: string = '';",
              "  @State backupFiles: string = '';\n  @State sayFreq: string = 'medium';")
s = s.replace("    await this.loadBackups();", "    await this.loadBackups();\n    await this.loadSayFreq();")
s = s.replace("  async loadBackups() {",
"""  async loadSayFreq() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/say/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 6000, readTimeout: 6000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.sayFreq = (d.freq ?? 'medium') as string;
      }
    } catch (e) { }
  }

  async saveSayFreq(f: string) {
    this.sayFreq = f;
    try {
      const req = http.createHttp();
      await req.request(`${this.baseUrl2}/api/say/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: `{"freq": "${f}"}`,
        connectTimeout: 6000, readTimeout: 6000,
      });
      req.destroy();
    } catch (e) { }
  }

  async loadBackups() {""")

# UI：功能开关卡片加说说频率行（网上冲浪之后）
s = s.replace("""            .width('100%').margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 备份与导出""",
"""            .width('100%').margin({ top: 10 })
            Row() {
              Column() {
                Text('说说频率').fontSize(13).fontColor('#e8eeff')
                Text('她自动发说说的频率').fontSize(10).fontColor('#5f6c96').margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Start)
              .layoutWeight(1)
              Text('少').fontSize(12)
                .fontColor(this.sayFreq === 'low' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.sayFreq === 'low' ? '#3b6ef5' : '#161b29')
                .borderRadius(10)
                .onClick(() => { this.saveSayFreq('low'); })
              Text('中').fontSize(12)
                .fontColor(this.sayFreq === 'medium' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.sayFreq === 'medium' ? '#3b6ef5' : '#161b29')
                .borderRadius(10)
                .margin({ left: 6 })
                .onClick(() => { this.saveSayFreq('medium'); })
              Text('多').fontSize(12)
                .fontColor(this.sayFreq === 'high' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.sayFreq === 'high' ? '#3b6ef5' : '#161b29')
                .borderRadius(10)
                .margin({ left: 6 })
                .onClick(() => { this.saveSayFreq('high'); })
            }
            .width('100%').margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 备份与导出""")
p.write_text(s, encoding="utf-8")
print("说说频率已加")