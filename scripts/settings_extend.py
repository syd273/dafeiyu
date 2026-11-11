import json
from pathlib import Path

# ===== 注册路由 =====
p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
for page in ["pages/StarMap", "pages/LifeLog"]:
    if page not in d["src"]:
        d["src"].append(page)
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("路由已注册:", d["src"])

# ===== Settings.ets 扩展 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

# 状态
s = s.replace("""  @State baseUrl: string = '';""",
"""  @State localUrl: string = '';
  @State cloudUrl: string = '';
  @State mode: string = 'local';
  @State herName: string = '安诗鱼';""")

# 读取
s = s.replace("""    this.baseUrl = await AppConfig.getBase(ctx);""",
"""    this.localUrl = await AppConfig.getLocal(ctx);
    this.cloudUrl = await AppConfig.getCloud(ctx);
    this.mode = await AppConfig.getMode(ctx);
    this.herName = await AppConfig.getName(ctx);""")

# 保存方法
s = s.replace("""  async saveBase() {
    const ctx = getContext(this) as Context;
    let url = this.baseUrl.trim();
    if (!url.startsWith('http')) {
      this.tip = '地址需要以 http:// 开头';
      return;
    }
    await AppConfig.setBase(ctx, url);
    this.tip = '已保存，返回聊天页生效';
  }""",
"""  async saveServer() {
    const ctx = getContext(this) as Context;
    if (this.localUrl && !this.localUrl.trim().startsWith('http')) {
      this.tip = '本地地址需要以 http:// 开头';
      return;
    }
    if (this.cloudUrl && !this.cloudUrl.trim().startsWith('http')) {
      this.tip = '云端地址需要以 http:// 开头';
      return;
    }
    await AppConfig.setLocal(ctx, this.localUrl);
    await AppConfig.setCloud(ctx, this.cloudUrl);
    await AppConfig.setMode(ctx, this.mode);
    this.tip = '服务器配置已保存，返回聊天页生效';
  }

  async saveName() {
    const ctx = getContext(this) as Context;
    if (!this.herName.trim()) {
      this.tip = '名字不能为空';
      return;
    }
    await AppConfig.setName(ctx, this.herName);
    this.tip = '名字已保存';
  }""")

# 服务器卡片替换
old_server = """          // 服务器
          Column() {
            Text('🌐  服务器地址').fontSize(12).fontColor('#7f95c8').width('100%')
            TextInput({ text: this.baseUrl, placeholder: 'http://电脑IP:8900' })
              .fontSize(14)
              .fontColor('#e8eeff')
              .backgroundColor('#161b29')
              .borderRadius(12)
              .margin({ top: 8 })
              .onChange((v: string) => { this.baseUrl = v; })
            Button('保存')
              .height(36).margin({ top: 10 }).width('100%')
              .backgroundColor('#232d47').fontSize(14).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { this.saveBase(); })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16)"""
new_server = """          // 服务器：本地 / 云端
          Column() {
            Text('🌐  服务器').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Text('本地')
                .fontSize(13)
                .fontColor(this.mode === 'local' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 16, right: 16, top: 7, bottom: 7 })
                .backgroundColor(this.mode === 'local' ? '#3b6ef5' : '#161b29')
                .borderRadius(16)
                .onClick(() => { this.mode = 'local'; })
              Text('云端')
                .fontSize(13)
                .fontColor(this.mode === 'cloud' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 16, right: 16, top: 7, bottom: 7 })
                .backgroundColor(this.mode === 'cloud' ? '#3b6ef5' : '#161b29')
                .borderRadius(16)
                .margin({ left: 10 })
                .onClick(() => { this.mode = 'cloud'; })
              Blank()
            }
            .width('100%')
            .margin({ top: 10 })

            Text('本地地址（局域网）').fontSize(11).fontColor('#5f6c96').width('100%').margin({ top: 12 })
            TextInput({ text: this.localUrl, placeholder: 'http://电脑IP:8900' })
              .fontSize(13)
              .fontColor('#e8eeff')
              .backgroundColor('#161b29')
              .borderRadius(12)
              .margin({ top: 6 })
              .onChange((v: string) => { this.localUrl = v; })

            Text('云端地址（公网服务器）').fontSize(11).fontColor('#5f6c96').width('100%').margin({ top: 10 })
            TextInput({ text: this.cloudUrl, placeholder: 'http://你的服务器:8900' })
              .fontSize(13)
              .fontColor('#e8eeff')
              .backgroundColor('#161b29')
              .borderRadius(12)
              .margin({ top: 6 })
              .onChange((v: string) => { this.cloudUrl = v; })

            Button('保存服务器配置')
              .height(36).margin({ top: 12 }).width('100%')
              .backgroundColor('#232d47').fontSize(14).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { this.saveServer(); })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16)"""
s = s.replace(old_server, new_server)

# 名字卡片（插在服务器卡片后）
s = s.replace("""          // 头像
          Column() {
            Text('👤  头像与形象')""",
"""          // 名字
          Column() {
            Text('🏷️  她的名字').fontSize(12).fontColor('#7f95c8').width('100%')
            TextInput({ text: this.herName, placeholder: '安诗鱼' })
              .fontSize(14)
              .fontColor('#e8eeff')
              .backgroundColor('#161b29')
              .borderRadius(12)
              .margin({ top: 8 })
              .onChange((v: string) => { this.herName = v; })
            Button('保存名字')
              .height(34).margin({ top: 10 }).width('100%')
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { this.saveName(); })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 头像
          Column() {
            Text('👤  头像与形象')""")

# 更多入口（插在表情包卡片后、tip 之前）
s = s.replace("""          if (this.tip) {
            Text(this.tip).fontSize(12).fontColor('#8fa2d8').margin({ top: 12 })
          }""",
"""          // 更多
          Column() {
            Text('✨  更多').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Button('记忆星图（横屏）')
                .height(36).layoutWeight(1)
                .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
                .borderRadius(12)
                .onClick(() => { router.pushUrl({ url: 'pages/StarMap' }); })
              Button('生活记录')
                .height(36).layoutWeight(1).margin({ left: 10 })
                .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
                .borderRadius(12)
                .onClick(() => { router.pushUrl({ url: 'pages/LifeLog' }); })
            }
            .width('100%')
            .margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          if (this.tip) {
            Text(this.tip).fontSize(12).fontColor('#8fa2d8').margin({ top: 12 })
          }""")

p.write_text(s, encoding="utf-8")
print("Settings 扩展完成")