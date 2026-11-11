// 设置页 v2：服务器、头像、外观（主题色 / 聊天背景）、自定义表情包
import router from '@ohos.router';
import http from '@ohos.net.http';
import { AppConfig, EmojiItem } from '../common/Config';
import { Notifier } from '../common/Notifier';
import { ChatStore, SyncState } from '../common/ChatStore';
import { PushHelper } from '../common/PushHelper';

let TOKEN = 'anshiyu-app-2026';

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
  @State talkative: number = 50;
  @State clingy: number = 50;
  @State gentle: number = 50;
  @State proactive: string = 'medium';
  @State memoryMode: string = 'decay';
  @State halfLifeDays: number = 1.08;
  @State maxEpisodes: number = 0;
  @State nightlyReflect: boolean = true;
  @State diagMsg: string = '';
  @State localTestMsg: string = '';
  @State cloudTestMsg: string = '';
  @State apiKeyInput: string = '';
  @State keyConfigured: boolean = false;
  @State keyMasked: string = '';
  @State keyMsg: string = '';
  @State featRoom: boolean = true;
  @State featStickers: boolean = true;
  @State featTrends: boolean = true;
  @State backupMsg: string = '';
  @State backupFiles: string = '';
  @State sayFreq: string = 'medium';
  @State tokenInput: string = '';
  @State tokenMsg: string = '';
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
    await this.loadPersona();
    await this.loadMemory();
    await this.loadApiKey();
    await this.loadFeatures();
    await this.loadBackups();
    await this.loadSayFreq();
    await this.loadToken();
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

  async loadApiKey() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/config/api-key?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 6000, readTimeout: 6000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.keyConfigured = (d.configured ?? false) as boolean;
        this.keyMasked = (d.masked ?? '') as string;
      }
    } catch (e) { }
  }

  async saveApiKey() {
    const k = this.apiKeyInput.trim();
    if (!k) { this.keyMsg = '请输入 API Key'; return; }
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/config/api-key?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ apiKey: k }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        this.keyConfigured = true;
        this.keyMasked = (d.masked ?? '') as string;
        this.apiKeyInput = '';
        this.keyMsg = '已保存（只存在你的电脑上）';
      } else {
        this.keyMsg = (d.error ?? '保存失败') as string;
      }
    } catch (e) {
      this.keyMsg = '保存失败，检查网络';
    }
  }

  async testApiKey() {
    this.keyMsg = '测试中…';
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/config/api-key/test?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 30000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      this.keyMsg = d.ok ? 'Key 可用 ✓' : `Key 不可用（${d.error ?? d.status ?? '未知'}）`;
    } catch (e) {
      this.keyMsg = '测试失败，检查网络';
    }
  }

  async testServer(url: string, which: string) {
    const u = url.trim();
    if (!u) return;
    const msg = which === 'local' ? 'localTestMsg' : 'cloudTestMsg';
    try {
      const req = http.createHttp();
      const res = await req.request(`${u}/api/status?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 4000, readTimeout: 4000,
      });
      req.destroy();
      const ok = res.responseCode === 200;
      if (which === 'local') { this.localTestMsg = ok ? '连接成功 ✓' : `连接失败（${res.responseCode}）`; }
      else { this.cloudTestMsg = ok ? '连接成功 ✓' : `连接失败（${res.responseCode}）`; }
    } catch (e) {
      if (which === 'local') { this.localTestMsg = '连接失败'; } else { this.cloudTestMsg = '连接失败'; }
    }
  }

  async loadFeatures() {
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

  async loadToken() {
    const ctx = getContext(this) as Context;
    this.tokenInput = await AppConfig.getToken(ctx);
    if (this.tokenInput) TOKEN = this.tokenInput;
  }

  async saveToken() {
    const ctx = getContext(this) as Context;
    await AppConfig.setToken(ctx, this.tokenInput);
    this.tokenMsg = '令牌已保存（重启 App 生效）';
  }

  async loadSayFreq() {
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

  async loadBackups() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/backup/list?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 6000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const items = (d.items ?? []) as Array<Record<string, Object>>;
        let text = '';
        for (let i = 0; i < Math.min(items.length, 3); i++) {
          const it = items[i];
          const kb = Math.round(((it.size ?? 0) as number) / 1024);
          text += `${it.file}（${kb} KB）\n`;
        }
        this.backupFiles = text;
      }
    } catch (e) { }
  }

  async backupNow() {
    this.backupMsg = '打包中…';
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/backup/export?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST, connectTimeout: 10000, readTimeout: 60000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        const kb = Math.round(((d.size ?? 0) as number) / 1024);
        this.backupMsg = `已备份：${d.file}（${kb} KB）\n电脑里：D:\\大肥鱼\\backups\\`;
        await this.loadBackups();
    await this.loadSayFreq();
    await this.loadToken();
      } else {
        this.backupMsg = '备份失败';
      }
    } catch (e) {
      this.backupMsg = '备份失败，检查网络';
    }
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

  async loadPersona() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/persona/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.talkative = (d.talkative ?? 50) as number;
        this.clingy = (d.clingy ?? 50) as number;
        this.gentle = (d.gentle ?? 50) as number;
        this.proactive = (d.proactive ?? 'medium') as string;
      }
    } catch (e) { }
  }

  async savePersona() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/persona/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({
          talkative: this.talkative, clingy: this.clingy, gentle: this.gentle,
          proactive: this.proactive,
        }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      this.tip = '她的性格已保存';
    } catch (e) {
      this.tip = '性格保存失败';
    }
  }

  async loadMemory() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/memory/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.memoryMode = (d.memoryMode ?? 'decay') as string;
        this.halfLifeDays = (d.halfLifeDays ?? 1.08) as number;
        this.maxEpisodes = (d.maxEpisodes ?? 0) as number;
        this.nightlyReflect = (d.nightlyReflect ?? true) as boolean;
      }
    } catch (e) { }
  }

  async saveMemory() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/memory/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({
          memoryMode: this.memoryMode, halfLifeDays: this.halfLifeDays,
          maxEpisodes: this.maxEpisodes, nightlyReflect: this.nightlyReflect,
        }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      this.tip = '记忆设置已保存';
    } catch (e) {
      this.tip = '记忆设置保存失败';
    }
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

  async clearChat() {
    const ctx = getContext(this) as Context;
    await ChatStore.clear(ctx);
    // 防止重启 App 时把旧主动消息补收回来
    await SyncState.set(ctx, Math.floor(Date.now() / 1000));
    // 重置离线同步游标，保持消息与服务器一致
    this.tip = '聊天记录已清空（她的记忆和星图都还在）';
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
            Button('推送诊断')
              .height(30).margin({ top: 8 }).width('100%')
              .backgroundColor('#161b29').fontSize(12).fontColor('#8fa2d8')
              .borderRadius(10)
              .onClick(() => {
                this.diagMsg = '检测中…';
                PushHelper.diagnose(this.baseUrl2).then((msg: string) => {
                  this.diagMsg = msg;
                }).catch((e: Error) => {
                  this.diagMsg = '检测异常: ' + e.message;
                });
              })
            if (this.diagMsg) {
              Text(this.diagMsg)
                .fontSize(11).fontColor('#ffd48a')
                .width('100%').margin({ top: 6 })
                .maxLines(3)
            }
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ bottom: 12 })

          // 本地服务器
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

          // 连接令牌
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
          .width('100%').constraintSize({ maxWidth: 680 }).padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

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

          // 她的性格
          Column() {
            Text('🎭  她的性格').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Text('话少').fontSize(11).fontColor('#5f6c96').width(30)
              Slider({ value: this.talkative, min: 0, max: 100, style: SliderStyle.OutSet })
                .layoutWeight(1)
                .selectedColor('#3b6ef5')
                .onChange((v: number, mode: SliderChangeMode) => {
                  this.talkative = Math.round(v);
                  if (mode === SliderChangeMode.End || mode === SliderChangeMode.Click) { this.savePersona(); }
                })
              Text('话多').fontSize(11).fontColor('#5f6c96').width(30)
            }
            .width('100%').margin({ top: 6 })
            Row() {
              Text('独立').fontSize(11).fontColor('#5f6c96').width(30)
              Slider({ value: this.clingy, min: 0, max: 100, style: SliderStyle.OutSet })
                .layoutWeight(1)
                .selectedColor('#8b5cf6')
                .onChange((v: number, mode: SliderChangeMode) => {
                  this.clingy = Math.round(v);
                  if (mode === SliderChangeMode.End || mode === SliderChangeMode.Click) { this.savePersona(); }
                })
              Text('黏人').fontSize(11).fontColor('#5f6c96').width(30)
            }
            .width('100%').margin({ top: 4 })
            Row() {
              Text('毒舌').fontSize(11).fontColor('#5f6c96').width(30)
              Slider({ value: this.gentle, min: 0, max: 100, style: SliderStyle.OutSet })
                .layoutWeight(1)
                .selectedColor('#ec4899')
                .onChange((v: number, mode: SliderChangeMode) => {
                  this.gentle = Math.round(v);
                  if (mode === SliderChangeMode.End || mode === SliderChangeMode.Click) { this.savePersona(); }
                })
              Text('温柔').fontSize(11).fontColor('#5f6c96').width(30)
            }
            .width('100%').margin({ top: 4 })
            Row() {
              Text('主动频率').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('少').fontSize(12)
                .fontColor(this.proactive === 'low' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.proactive === 'low' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.proactive = 'low'; this.savePersona(); })
              Text('中').fontSize(12)
                .fontColor(this.proactive === 'medium' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.proactive === 'medium' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.proactive = 'medium'; this.savePersona(); })
              Text('多').fontSize(12)
                .fontColor(this.proactive === 'high' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.proactive === 'high' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.proactive = 'high'; this.savePersona(); })
            }
            .width('100%').margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 记忆设置
          Column() {
            Text('🧠  记忆设置').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Text('记忆模式').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('完全').fontSize(12)
                .fontColor(this.memoryMode === 'full' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.memoryMode === 'full' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.memoryMode = 'full'; this.saveMemory(); })
              Text('衰减').fontSize(12)
                .fontColor(this.memoryMode === 'decay' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.memoryMode === 'decay' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.memoryMode = 'decay'; this.saveMemory(); })
            }
            .width('100%').margin({ top: 10 })
            Row() {
              Text('遗忘速度').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('慢').fontSize(12)
                .fontColor(this.halfLifeDays >= 2 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.halfLifeDays >= 2 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.halfLifeDays = 3; this.saveMemory(); })
              Text('中').fontSize(12)
                .fontColor(this.halfLifeDays > 0.6 && this.halfLifeDays < 2 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.halfLifeDays > 0.6 && this.halfLifeDays < 2 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.halfLifeDays = 1.08; this.saveMemory(); })
              Text('快').fontSize(12)
                .fontColor(this.halfLifeDays <= 0.6 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.halfLifeDays <= 0.6 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.halfLifeDays = 0.5; this.saveMemory(); })
            }
            .width('100%').margin({ top: 8 })
            Row() {
              Text('记忆上限').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('500').fontSize(12)
                .fontColor(this.maxEpisodes === 500 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.maxEpisodes === 500 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.maxEpisodes = 500; this.saveMemory(); })
              Text('1000').fontSize(12)
                .fontColor(this.maxEpisodes === 1000 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.maxEpisodes === 1000 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.maxEpisodes = 1000; this.saveMemory(); })
              Text('不限').fontSize(12)
                .fontColor(this.maxEpisodes === 0 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.maxEpisodes === 0 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.maxEpisodes = 0; this.saveMemory(); })
            }
            .width('100%').margin({ top: 8 })
            Row() {
              Text('夜间反思').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Toggle({ type: ToggleType.Switch, isOn: this.nightlyReflect })
                .selectedColor('#3b6ef5')
                .onChange((v: boolean) => { this.nightlyReflect = v; this.saveMemory(); })
            }
            .width('100%').margin({ top: 8 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 聊天记录
          Column() {
            Text('💬  聊天记录').fontSize(12).fontColor('#7f95c8').width('100%')
            Button('清空聊天记录（保留她的记忆）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#3a2530').fontSize(13).fontColor('#ffb4b4')
              .borderRadius(12)
              .onClick(() => { this.clearChat(); })
            Text('只清空本机聊天界面，她的记忆、星图、日记都不会删')
              .fontSize(11).fontColor('#5f6c96').margin({ top: 8 })
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

          // 功能开关
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

          // 备份与导出
          Column() {
            Text('💾  备份与导出').fontSize(12).fontColor('#7f95c8').width('100%')
            Text('把她的记忆、聊天、日记、传承打包成一个 zip（存在电脑上）')
              .fontSize(10).fontColor('#5f6c96').margin({ top: 6 }).width('100%')
            Button('立即备份')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { this.backupNow(); })
            if (this.backupMsg) {
              Text(this.backupMsg).fontSize(11).fontColor('#ffd48a').margin({ top: 8 }).width('100%').maxLines(3)
            }
            if (this.backupFiles) {
              Text('最近备份：').fontSize(10).fontColor('#5f6c96').margin({ top: 8 }).width('100%')
              Text(this.backupFiles).fontSize(10).fontColor('#8fa2d8').width('100%').maxLines(4)
            }
            Text('⚠️ 备份含聊天隐私，请妥善保存；恢复时解压覆盖对应目录')
              .fontSize(10).fontColor('#4a567c').margin({ top: 8 }).width('100%')
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
            Button('🎧 一起听歌')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Music' }); })
            Button('🕯️ 她的传承')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Legacy' }); })
            Button('🌅 上帝视角（看她的生活）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/GodView' }); })
            Button('💬 她的说说')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Says' }); })
            Button('📖 配置教程（从注册到可用）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Guide' }); })
            Button('🔒 隐私政策')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Privacy' }); })
            Button('📄 用户协议')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Agreement' }); })
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
      .edgeEffect(EdgeEffect.Spring)
      .layoutWeight(1)
    }
    .padding({ top: 38 })
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
