// 设置页 v2：服务器、头像、外观（主题色 / 聊天背景）、自定义表情包
import router from '@ohos.router';
import http from '@ohos.net.http';
import { AppConfig, EmojiItem } from '../common/Config';
import { Notifier } from '../common/Notifier';

const THEMES: string[] = ['#3b6ef5', '#8b5cf6', '#06b6d4', '#22c55e', '#f97316', '#ec4899'];
const THEME_NAMES: string[] = ['蓝', '紫', '青', '绿', '橙', '粉'];

interface BgOption {
  key: string;
  name: string;
  from: string;
  to: string;
}

const BGS: BgOption[] = [
  { key: 'default', name: '深空', from: '#0d1017', to: '#0d1017' },
  { key: 'night', name: '星夜', from: '#0b1020', to: '#131a2e' },
  { key: 'gray', name: '极简', from: '#101114', to: '#16181d' },
  { key: 'warm', name: '暖夜', from: '#171310', to: '#211812' }
];

@Entry
@Component
struct Settings {
  @State localUrl: string = '';
  @State cloudUrl: string = '';
  @State mode: string = 'local';
  @State herName: string = '安诗鱼';
  @State sharePref: string = 'both';
  @State baseUrl2: string = '';
  @State myAvatar: string = '';
  @State herAvatar: string = '';
  @State emojis: EmojiItem[] = [];
  @State theme: string = '#3b6ef5';
  @State bgKey: string = 'default';
  @State bgImage: string = '';
  @State tip: string = '';

  aboutToAppear() {
    this.loadAll();
  }

  async loadAll() {
    const ctx = getContext(this) as Context;
    this.localUrl = await AppConfig.getLocal(ctx);
    this.cloudUrl = await AppConfig.getCloud(ctx);
    this.mode = await AppConfig.getMode(ctx);
    this.herName = await AppConfig.getName(ctx);
    this.baseUrl2 = await AppConfig.getBase(ctx);
    await this.loadSharePref();
    this.myAvatar = await AppConfig.getAvatar(ctx, 'me');
    this.herAvatar = await AppConfig.getAvatar(ctx, 'her');
    this.emojis = await AppConfig.getEmojis(ctx);
    this.theme = await AppConfig.getTheme(ctx);
    this.bgKey = await AppConfig.getBg(ctx);
    this.bgImage = await AppConfig.getBgImage(ctx);
  }

  async saveServer() {
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

  async loadSharePref() {
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
        this.tip = '保存失败';
      }
    } catch (e) {
      this.tip = '保存失败，检查服务器';
    }
  }

  async saveName() {
    const ctx = getContext(this) as Context;
    if (!this.herName.trim()) {
      this.tip = '名字不能为空';
      return;
    }
    await AppConfig.setName(ctx, this.herName);
    this.tip = '名字已保存';
  }

  async changeAvatar(who: string) {
    try {
      const ctx = getContext(this) as Context;
      const path = await AppConfig.pickAvatar(ctx, who);
      if (path) {
        if (who === 'me') this.myAvatar = path;
        else this.herAvatar = path;
        this.tip = '头像已更换';
      }
    } catch (e) {
      this.tip = '选择图片失败：' + JSON.stringify(e);
    }
  }

  async selectTheme(color: string) {
    const ctx = getContext(this) as Context;
    this.theme = color;
    await AppConfig.setTheme(ctx, color);
    this.tip = '主题色已更换';
  }

  async selectBg(key: string) {
    const ctx = getContext(this) as Context;
    this.bgKey = key;
    await AppConfig.setBg(ctx, key);
    this.tip = '聊天背景已更换';
  }

  async pickBg() {
    try {
      const ctx = getContext(this) as Context;
      const path = await AppConfig.pickBgImage(ctx);
      if (path) {
        this.bgImage = path;
        this.bgKey = 'custom';
        this.tip = '已使用自定义背景图';
      }
    } catch (e) {
      this.tip = '选择背景失败：' + JSON.stringify(e);
    }
  }

  async addEmojis() {
    try {
      const ctx = getContext(this) as Context;
      this.emojis = await AppConfig.addEmojis(ctx);
      this.tip = `已有 ${this.emojis.length} 个自定义表情`;
    } catch (e) {
      this.tip = '添加表情失败：' + JSON.stringify(e);
    }
  }

  async deleteEmoji(file: string) {
    const ctx = getContext(this) as Context;
    this.emojis = await AppConfig.removeEmoji(ctx, file);
    this.tip = '已删除';
  }

  @Builder
  avatarRow(title: string, path: string, who: string) {
    Row() {
      Text(title).fontSize(15).fontColor('#e8eeff').layoutWeight(1)
      if (path) {
        Image('file://' + path)
          .width(44).height(44).borderRadius(12)
          .border({ width: 1, color: '#2b3b66' })
      } else {
        Text('未设置')
          .fontSize(12).fontColor('#5f6c96')
          .width(44).height(44).textAlign(TextAlign.Center)
      }
      Text('›').fontSize(18).fontColor('#4a567c').margin({ left: 8 })
      Button('更换')
        .height(32).margin({ left: 8 })
        .fontSize(13)
        .fontColor('#cfe0ff')
        .backgroundColor('#232d47')
        .borderRadius(10)
        .onClick(() => { this.changeAvatar(who); })
    }
    .width('100%')
    .padding({ top: 10, bottom: 10 })
  }

  build() {
    Column() {
      // 标题栏
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('设置').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
      }
      .width('100%')
      .padding({ left: 8, right: 14, top: 10, bottom: 10 })
      .backgroundColor('#11151f')

      Scroll() {
        Column() {
          // 通知测试
          Column() {
            Row() {
              Text('🔔  通知').fontSize(12).fontColor('#7f95c8').layoutWeight(1)
              Button('发送测试通知')
                .height(32).fontSize(13).fontColor('#cfe0ff')
                .backgroundColor('#232d47').borderRadius(10)
                .onClick(() => { Notifier.notify('安诗鱼', '这是一条测试通知，收到就说明通知正常。'); })
            }
            .width('100%')
            Text('收不到的话，去系统设置里允许安诗鱼通知')
              .fontSize(11).fontColor('#5f6c96').margin({ top: 8 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ bottom: 12 })

          // 服务器：本地 / 云端
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
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16)

          // 名字
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
            Text('👤  头像与形象').fontSize(12).fontColor('#7f95c8').width('100%')
            this.avatarRow('我的头像', this.myAvatar, 'me')
            Divider().color('#1e2840').strokeWidth(0.5)
            this.avatarRow('安诗鱼的头像', this.herAvatar, 'her')
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 外观：主题色
          Column() {
            Text('🎨  主题颜色').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              ForEach(THEMES, (c: string, i: number) => {
                Column() {
                  Circle({ width: 30, height: 30 })
                    .fill(c)
                    .stroke(this.theme === c ? '#ffffff' : '#00000000')
                    .strokeWidth(2)
                  Text(THEME_NAMES[i]).fontSize(10).fontColor('#6f7fae').margin({ top: 4 })
                }
                .margin({ right: 14 })
                .onClick(() => { this.selectTheme(c); })
              }, (c: string) => c)
            }
            .width('100%')
            .margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 外观：聊天背景
          Column() {
            Text('🖼️  聊天背景').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              ForEach(BGS, (b: BgOption) => {
                Column() {
                  Row()
                    .width(52).height(52)
                    .borderRadius(12)
                    .linearGradient({ angle: 160, colors: [[b.from, 0], [b.to, 1]] })
                    .border({ width: this.bgKey === b.key ? 2 : 1, color: this.bgKey === b.key ? '#ffffff' : '#2b3350' })
                  Text(b.name).fontSize(10).fontColor('#6f7fae').margin({ top: 4 })
                }
                .margin({ right: 12 })
                .onClick(() => { this.selectBg(b.key); })
              }, (b: BgOption) => b.key)
              Column() {
                if (this.bgImage) {
                  Image('file://' + this.bgImage)
                    .width(52).height(52).borderRadius(12)
                    .border({ width: this.bgKey === 'custom' ? 2 : 1, color: this.bgKey === 'custom' ? '#ffffff' : '#2b3350' })
                } else {
                  Row()
                    .width(52).height(52).borderRadius(12)
                    .backgroundColor('#1a2138')
                    .border({ width: 1, color: '#2b3350' })
                    .justifyContent(FlexAlign.Center)
                  Text('＋').fontSize(20).fontColor('#7f95c8')
                    .position({ x: 18, y: 14 })
                }
                Text('相册').fontSize(10).fontColor('#6f7fae').margin({ top: 4 })
              }
              .onClick(() => { this.pickBg(); })
            }
            .width('100%')
            .margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 表情包
          Column() {
            Row() {
              Text('😊  自定义表情包').fontSize(12).fontColor('#7f95c8').layoutWeight(1)
              Button('＋ 添加')
                .height(30).fontSize(13).fontColor('#cfe0ff')
                .backgroundColor('#232d47').borderRadius(10)
                .onClick(() => { this.addEmojis(); })
            }
            .width('100%')
            if (this.emojis.length === 0) {
              Text('还没有自定义表情，点「添加」从相册选图片')
                .fontSize(12).fontColor('#5f6c96')
                .margin({ top: 10 })
            } else {
              Grid() {
                ForEach(this.emojis, (e: EmojiItem) => {
                  GridItem() {
                    Stack({ alignContent: Alignment.TopEnd }) {
                      Image('file://' + e.file)
                        .width(64).height(64).borderRadius(12)
                        .border({ width: 1, color: '#2b3350' })
                      Text('×')
                        .fontSize(14).fontColor('#ffffff')
                        .width(20).height(20).textAlign(TextAlign.Center)
                        .backgroundColor('#c0392b').borderRadius(10)
                        .onClick(() => { this.deleteEmoji(e.file); })
                    }
                  }
                }, (e: EmojiItem) => e.file)
              }
              .columnsTemplate('1fr 1fr 1fr 1fr')
              .height(160)
              .margin({ top: 10 })
            }
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 她的内容来源
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
            Button('记忆记录（可搜索/删除）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/MemoryRecords' }); })
            Row() {
            }
            .width('100%')
            .margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          if (this.tip) {
            Text(this.tip).fontSize(12).fontColor('#8fa2d8').margin({ top: 12 })
          }

          Text('返回聊天页后生效').fontSize(11).fontColor('#4a567c').margin({ top: 18, bottom: 24 })
        }
        .padding({ left: 14, right: 14, top: 14 })
      }
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
