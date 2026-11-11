from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

start = s.find("          // 服务器：本地 / 云端")
end = s.find("          // 名字", start)
if start < 0 or end < 0:
    print("未找到原服务器卡片，start=", start, "end=", end)
else:
    new_ui = '''          // 本地服务器
          Column() {
            Row() {
              Text('🏠  本地服务器（局域网）').fontSize(12).fontColor('#7f95c8')
              Blank()
              Text(this.mode === 'local' ? '✅ 当前使用' : '使用这个')
                .fontSize(12)
                .fontColor(this.mode === 'local' ? '#7ee0a3' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 4, bottom: 4 })
                .backgroundColor(this.mode === 'local' ? '#163a2a' : '#161b29')
                .borderRadius(10)
                .onClick(() => { this.mode = 'local'; this.saveServer(); })
            }
            .width('100%')

            TextInput({ text: this.localUrl, placeholder: 'http://电脑IP:8900' })
              .fontSize(13).fontColor('#e8eeff').backgroundColor('#161b29').borderRadius(12)
              .margin({ top: 8 })
              .onChange((v: string) => { this.localUrl = v; })

            Row() {
              Button('测试连接')
                .height(32).layoutWeight(1)
                .backgroundColor('#232d47').fontSize(12).fontColor('#cfe0ff')
                .borderRadius(10)
                .onClick(() => { this.testServer(this.localUrl, 'local'); })
              Button('保存本地')
                .height(32).layoutWeight(1).margin({ left: 8 })
                .backgroundColor('#3b6ef5').fontSize(12).fontColor('#ffffff')
                .borderRadius(10)
                .onClick(() => { this.saveServer(); this.localTestMsg = '已保存本地地址'; })
            }
            .width('100%').margin({ top: 8 })

            if (this.localTestMsg) {
              Text(this.localTestMsg).fontSize(11).fontColor('#ffd48a').margin({ top: 6 })
            }
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ bottom: 12 })

          // 云端服务器
          Column() {
            Row() {
              Text('☁️  云端服务器（公网）').fontSize(12).fontColor('#7f95c8')
              Blank()
              Text(this.mode === 'cloud' ? '✅ 当前使用' : '使用这个')
                .fontSize(12)
                .fontColor(this.mode === 'cloud' ? '#7ee0a3' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 4, bottom: 4 })
                .backgroundColor(this.mode === 'cloud' ? '#163a2a' : '#161b29')
                .borderRadius(10)
                .onClick(() => { this.mode = 'cloud'; this.saveServer(); })
            }
            .width('100%')

            TextInput({ text: this.cloudUrl, placeholder: 'http://你的服务器:8900' })
              .fontSize(13).fontColor('#e8eeff').backgroundColor('#161b29').borderRadius(12)
              .margin({ top: 8 })
              .onChange((v: string) => { this.cloudUrl = v; })

            Row() {
              Button('测试连接')
                .height(32).layoutWeight(1)
                .backgroundColor('#232d47').fontSize(12).fontColor('#cfe0ff')
                .borderRadius(10)
                .onClick(() => { this.testServer(this.cloudUrl, 'cloud'); })
              Button('保存云端')
                .height(32).layoutWeight(1).margin({ left: 8 })
                .backgroundColor('#3b6ef5').fontSize(12).fontColor('#ffffff')
                .borderRadius(10)
                .onClick(() => { this.saveServer(); this.cloudTestMsg = '已保存云端地址'; })
            }
            .width('100%').margin({ top: 8 })

            if (this.cloudTestMsg) {
              Text(this.cloudTestMsg).fontSize(11).fontColor('#ffd48a').margin({ top: 6 })
            }
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ bottom: 12 })

          // DeepSeek API Key
          Column() {
            Row() {
              Text('🔑  DeepSeek API Key').fontSize(12).fontColor('#7f95c8')
              Blank()
              Text(this.keyConfigured ? '已配置' : '未配置')
                .fontSize(11)
                .fontColor(this.keyConfigured ? '#7ee0a3' : '#ff9b9b')
            }
            .width('100%')

            if (this.keyConfigured) {
              Text('当前：' + this.keyMasked).fontSize(11).fontColor('#5f6c96').margin({ top: 6 }).width('100%')
            }

            TextInput({ text: this.apiKeyInput, placeholder: 'sk-...（粘贴你的 API Key）' })
              .type(InputType.Password)
              .fontSize(13).fontColor('#e8eeff').backgroundColor('#161b29').borderRadius(12)
              .margin({ top: 8 })
              .onChange((v: string) => { this.apiKeyInput = v; })

            Row() {
              Button('保存 Key')
                .height(32).layoutWeight(1)
                .backgroundColor('#3b6ef5').fontSize(12).fontColor('#ffffff')
                .borderRadius(10)
                .onClick(() => { this.saveApiKey(); })
              Button('测试 Key')
                .height(32).layoutWeight(1).margin({ left: 8 })
                .backgroundColor('#232d47').fontSize(12).fontColor('#cfe0ff')
                .borderRadius(10)
                .onClick(() => { this.testApiKey(); })
            }
            .width('100%').margin({ top: 8 })

            if (this.keyMsg) {
              Text(this.keyMsg).fontSize(11).fontColor('#ffd48a').margin({ top: 6 })
            }
            Text('Key 只保存在你的电脑上（文件权限已限制），App 不存明文')
              .fontSize(10).fontColor('#4a567c').margin({ top: 8 }).width('100%')
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ bottom: 12 })

          '''
    s = s[:start] + new_ui + s[end:]
    p.write_text(s, encoding="utf-8")
    print("服务器与 Key 卡片已替换")