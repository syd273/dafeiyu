from pathlib import Path

# 1) AppConfig 加 token
p = Path(r"D:\anshiyu_app\entry\src\main\ets\common\Config.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("const KEY_BG_IMAGE = 'chat_bg_image';",
              "const KEY_BG_IMAGE = 'chat_bg_image';\nconst KEY_TOKEN = 'api_token';")
s = s.replace("""  // ===== 名字 =====""",
"""  // ===== 连接令牌 =====
  static async getToken(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_TOKEN, '')) as string;
    } catch (e) {
      return '';
    }
  }

  static async setToken(ctx: Context, token: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_TOKEN, token.trim());
    await p.flush();
  }

  // ===== 名字 =====""")
p.write_text(s, encoding="utf-8")
print("AppConfig token 已加")

# 2) 设置页加 token 输入 + 教程入口（更多里）
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State sayFreq: string = 'medium';",
              "  @State sayFreq: string = 'medium';\n  @State tokenInput: string = '';\n  @State tokenMsg: string = '';")
s = s.replace("    await this.loadSayFreq();", "    await this.loadSayFreq();\n    await this.loadToken();")
s = s.replace("  async loadSayFreq() {",
"""  async loadToken() {
    const ctx = getContext(this) as Context;
    this.tokenInput = await AppConfig.getToken(ctx);
  }

  async saveToken() {
    const ctx = getContext(this) as Context;
    await AppConfig.setToken(ctx, this.tokenInput);
    this.tokenMsg = '令牌已保存（重启 App 生效）';
  }

  async loadSayFreq() {""")

# 2.1 服务器卡片里加令牌输入（本地/云端之后，API Key 卡片之前）
s = s.replace("""          // DeepSeek API Key""",
"""          // 连接令牌
          Column() {
            Text('🔐  连接令牌').fontSize(12).fontColor('#7f95c8').width('100%')
            TextInput({ text: this.tokenInput, placeholder: '服务器 config.json 里的 token' })
              .type(InputType.Password)
              .fontSize(13).fontColor('#e8eeff').backgroundColor('#161b29').borderRadius(12)
              .margin({ top: 8 })
              .onChange((v: string) => { this.tokenInput = v; })
            Button('保存令牌')
              .height(32).width('100%').margin({ top: 8 })
              .backgroundColor('#232d47').fontSize(12).fontColor('#cfe0ff')
              .borderRadius(10)
              .onClick(() => { this.saveToken(); })
            if (this.tokenMsg) {
              Text(this.tokenMsg).fontSize(11).fontColor('#ffd48a').margin({ top: 6 }).width('100%')
            }
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ bottom: 12 })

          // DeepSeek API Key""")

# 2.2 更多里加教程按钮
s = s.replace("""            Button('💬 她的说说')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Says' }); })""",
"""            Button('💬 她的说说')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Says' }); })
            Button('📖 配置教程（从注册到可用）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Guide' }); })""")
p.write_text(s, encoding="utf-8")
print("设置页 token 与教程入口已加")