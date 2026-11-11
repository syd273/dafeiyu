from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

s = s.replace("import router from '@ohos.router';",
"""import router from '@ohos.router';
import http from '@ohos.net.http';""")

s = s.replace("  @State herName: string = '安诗鱼';",
"""  @State herName: string = '安诗鱼';
  @State sharePref: string = 'both';
  @State baseUrl2: string = '';""")

# loadAll 末尾读取平台配置
s = s.replace("""    this.herName = await AppConfig.getName(ctx);""",
"""    this.herName = await AppConfig.getName(ctx);
    this.baseUrl2 = await AppConfig.getBase(ctx);
    await this.loadSharePref();""")

# 方法：读取/保存平台
s = s.replace("""  async saveName() {""",
"""  async loadSharePref() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/share/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.sharePref = (d.platform ?? 'both') as string;
      }
    } catch (e) { }
  }

  async saveSharePref(p: string) {
    this.sharePref = p;
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/share/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ platform: p }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        this.tip = '内容来源已保存';
      } else {
        this.tip = '保存失败');
      }
    } catch (e) {
      this.tip = '保存失败，检查服务器';
    }
  }

  async saveName() {""")

# UI：在"更多"卡片前插入内容来源卡片
s = s.replace("""          // 更多
          Column() {
            Text('✨  更多')""",
"""          // 她的内容来源
          Column() {
            Text('📺  她的内容来源').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Text('都看')
                .fontSize(13)
                .fontColor(this.sharePref === 'both' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 16, right: 16, top: 7, bottom: 7 })
                .backgroundColor(this.sharePref === 'both' ? '#3b6ef5' : '#161b29')
                .borderRadius(16)
                .onClick(() => { this.saveSharePref('both'); })
              Text('B站')
                .fontSize(13)
                .fontColor(this.sharePref === 'bili' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 16, right: 16, top: 7, bottom: 7 })
                .backgroundColor(this.sharePref === 'bili' ? '#3b6ef5' : '#161b29')
                .borderRadius(16)
                .margin({ left: 10 })
                .onClick(() => { this.saveSharePref('bili'); })
              Text('抖音')
                .fontSize(13)
                .fontColor(this.sharePref === 'douyin' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 16, right: 16, top: 7, bottom: 7 })
                .backgroundColor(this.sharePref === 'douyin' ? '#3b6ef5' : '#161b29')
                .borderRadius(16)
                .margin({ left: 10 })
                .onClick(() => { this.saveSharePref('douyin'); })
              Blank()
            }
            .width('100%')
            .margin({ top: 10 })
            Text('控制她主动分享时刷哪个平台的内容')
              .fontSize(11).fontColor('#5f6c96').margin({ top: 8 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 更多
          Column() {
            Text('✨  更多')""")

p.write_text(s, encoding="utf-8")
print("设置页内容来源已加")