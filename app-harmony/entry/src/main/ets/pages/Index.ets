// 安诗鱼 · 主容器（组件化后的轻量壳：只持有数据和业务逻辑）
import http from '@ohos.net.http';
import webSocket from '@ohos.net.webSocket';
import router from '@ohos.router';
import { AppConfig, EmojiItem } from '../common/Config';
import { TopBar } from '../components/TopBar';
import { ChatInput } from '../components/ChatInput';
import { EmojiPanel } from '../components/EmojiPanel';
import { MessageList, ChatMsg } from '../components/MessageList';
import { ChatStore, StoredMsg, SyncState } from '../common/ChatStore';
import { photoAccessHelper } from '@kit.MediaLibraryKit';
import fs from '@ohos.file.fs';
import { Notifier } from '../common/Notifier';
import { common } from '@kit.AbilityKit';

const TOKEN = 'anshiyu-app-2026';
const DEFAULT_BASE = 'http://192.168.43.5:8900';

@Entry
@Component
struct Index {
  @State messages: ChatMsg[] = [];
  @State sending: boolean = false;
  @State online: boolean = false;
  @State mood: string = '平静';
  @State life: string = '';
  @State showEmoji: boolean = false;
  @State draft: string = '';
  @State baseUrl: string = DEFAULT_BASE;
  @State theme: string = '#3b6ef5';
  @State bgKey: string = 'default';
  @State bgImage: string = '';
  @State myAvatar: string = '';
  @State herAvatar: string = '';
  @State herName: string = '安诗鱼';
  @State customEmojis: EmojiItem[] = [];
  @State showSplash: boolean = true;
  @State splashOpacity: number = 1;
  @State logoOpacity: number = 0;
  @State logoScale: number = 0.86;
  @State titleOpacity: number = 0;
  @State titleOffset: number = 14;
  private splashStart: number = 0;
  private ws: webSocket.WebSocket | null = null;
  private lastAssistant: string = '';
  private lastAssistantTs: number = 0;
  private pageVisible: boolean = true;

  aboutToAppear() {
    this.splashStart = Date.now();
    this.startSplash();
    Notifier.ensure(getContext(this) as common.UIAbilityContext);
    this.loadHistory();
    this.syncRecent();
    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
      this.finishSplash();
    }).catch(() => { this.finishSplash(); });
    setTimeout(() => { this.finishSplash(); }, 1200);
  }

  onPageShow() {
    this.pageVisible = true;
    this.loadConfig().then(() => { this.loadStatus(); });
  }

  onPageHide() {
    this.pageVisible = false;
  }

  aboutToDisappear() {
    try { this.ws?.close(); } catch (e) { }
  }

  /** 打开 App 时同步她之前发过的主动消息（离线补消息） */
  async syncRecent() {
    try {
      const ctx = getContext(this) as Context;
      const since = await SyncState.get(ctx);
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/messages/recent?token=${TOKEN}&since=${since}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 10000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const items = (d.items ?? []) as Array<Record<string, Object>>;
        for (const it of items) {
          const text = (it.text ?? '') as string;
          if (!text) continue;
          this.addMsg('assistant', text);
        }
        await SyncState.set(ctx, Math.floor(Date.now() / 1000));
      }
    } catch (e) { }
  }

  async loadHistory() {
    try {
      const ctx = getContext(this) as Context;
      const list = await ChatStore.load(ctx);
      if (list && list.length > 0) {
        this.messages = list;
      }
    } catch (e) { }
  }

  startSplash() {
    this.getUIContext().animateTo({ duration: 600, curve: Curve.EaseOut, delay: 80 }, () => {
      this.logoOpacity = 1;
      this.logoScale = 1;
    });
    this.getUIContext().animateTo({ duration: 420, curve: Curve.EaseOut, delay: 300 }, () => {
      this.titleOpacity = 1;
      this.titleOffset = 0;
    });
  }

  finishSplash() {
    if (!this.showSplash) return;
    const wait = Math.max(0, 800 - (Date.now() - this.splashStart));
    setTimeout(() => {
      this.getUIContext().animateTo({ duration: 300, curve: Curve.EaseInOut }, () => {
        this.splashOpacity = 0;
      });
      setTimeout(() => { this.showSplash = false; }, 320);
    }, wait);
  }

  async loadConfig() {
    const ctx = getContext(this) as Context;
    this.baseUrl = await AppConfig.getBase(ctx);
    this.myAvatar = await AppConfig.getAvatar(ctx, 'me');
    this.herAvatar = await AppConfig.getAvatar(ctx, 'her');
    this.herName = await AppConfig.getName(ctx);
    this.customEmojis = await AppConfig.getEmojis(ctx);
    this.theme = await AppConfig.getTheme(ctx);
    this.bgKey = await AppConfig.getBg(ctx);
    this.bgImage = await AppConfig.getBgImage(ctx);
  }

  bgFrom(): string {
    if (this.bgKey === 'night') return '#0b1020';
    if (this.bgKey === 'gray') return '#101114';
    if (this.bgKey === 'warm') return '#171310';
    return '#0d1017';
  }

  bgTo(): string {
    if (this.bgKey === 'night') return '#131a2e';
    if (this.bgKey === 'gray') return '#16181d';
    if (this.bgKey === 'warm') return '#211812';
    return '#0d1017';
  }

  wsUrl(): string {
    return this.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
  }

  async loadStatus() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/status?token=${TOKEN}`, {
        method: http.RequestMethod.GET,
        connectTimeout: 8000,
        readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const lifeObj = (d.life ?? {}) as Record<string, string>;
        this.mood = (d.mood ?? '平静') as string;
        this.life = `${lifeObj.location ?? ''} ${lifeObj.activity ?? ''}`;
        this.online = true;
      }
    } catch (e) {
      this.online = false;
    }
  }

  connectWs() {
    try { this.ws?.close(); } catch (e) { }
    try {
      this.ws = webSocket.createWebSocket();
      this.ws.on('open', () => { this.online = true; });
      this.ws.on('message', (err: Error, data: string | ArrayBuffer) => {
        if (err) return;
        try {
          const m = JSON.parse(data as string) as Record<string, string>;
          if (m.type === 'message' && m.role === 'assistant' && m.text) {
            this.addMsg('assistant', m.text);
            if (!this.pageVisible) {
              Notifier.notify('安诗鱼', m.text);
            }
          }
        } catch (e) { }
      });
      this.ws.on('close', () => { this.online = false; });
      this.ws.on('error', () => { this.online = false; });
      this.ws.connect(`${this.wsUrl()}/ws?token=${TOKEN}`);
    } catch (e) {
      this.online = false;
    }
  }

  addMsg(role: string, text: string, status: string = 'ok') {
    if (role === 'assistant') {
      const now = Date.now();
      if (text === this.lastAssistant && now - this.lastAssistantTs < 3000) return;
      this.lastAssistant = text;
      this.lastAssistantTs = now;
    }
    this.messages = this.messages.concat([{ role: role, text: text, ts: Date.now(), status: status }]);
    this.saveHistory();
  }

  setStatus(idx: number, status: string) {
    if (idx < 0 || idx >= this.messages.length) return;
    const arr = this.messages.slice();
    const m = arr[idx];
    arr[idx] = { role: m.role, text: m.text, ts: m.ts, status: status };
    this.messages = arr;
    this.saveHistory();
  }

  saveHistory() {
    const ctx = getContext(this) as Context;
    ChatStore.save(ctx, this.messages as StoredMsg[]);
  }

  removeAt(idx: number) {
    const arr = this.messages.slice();
    if (idx >= 0 && idx < arr.length) {
      arr.splice(idx, 1);
      this.messages = arr;
      this.saveHistory();
    }
  }

  async postChat(t: string): Promise<boolean> {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/chat?token=${TOKEN}`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ text: t }),
        connectTimeout: 8000,
        readTimeout: 60000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      const reply = d.reply as string;
      if (reply) this.addMsg('assistant', reply);
      if (d.life) {
        const lifeObj = d.life as Record<string, string>;
        this.mood = (d.mood ?? '平静') as string;
        this.life = `${lifeObj.location ?? ''} ${lifeObj.activity ?? ''}`;
      }
      return true;
    } catch (e) {
      this.addMsg('assistant', '（连接失败，请检查设置里的服务器地址或网络）');
      return false;
    }
  }

  async sendText(t: string) {
    const text = t.trim();
    if (!text || this.sending) return;
    this.showEmoji = false;
    const idx = this.messages.length;
    this.addMsg('user', text, 'sending');
    this.sending = true;
    const ok = await this.postChat(text);
    this.setStatus(idx, ok ? 'ok' : 'failed');
    this.sending = false;
  }

  /** 图片消息 */
  async pickImageAndSend() {
    if (this.sending) return;
    try {
      const picker = new photoAccessHelper.PhotoViewPicker();
      const opts: photoAccessHelper.PhotoSelectOptions = {
        MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE,
        maxSelectNumber: 1,
      };
      const res = await picker.select(opts);
      if (!res.photoUris || res.photoUris.length === 0) return;
      const ctx = getContext(this) as Context;
      const dst = `${ctx.filesDir}/sent_${Date.now()}.png`;
      const inFile = fs.openSync(res.photoUris[0], fs.OpenMode.READ_ONLY);
      const outFile = fs.openSync(dst, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
      fs.copyFileSync(inFile.fd, outFile.fd);
      fs.closeSync(inFile);
      fs.closeSync(outFile);
      this.showEmoji = false;
      const idx = this.messages.length;
      this.addMsg('user', `[img:${dst}]`, 'sending');
      this.sending = true;
      const ok = await this.postChat('[图片]');
      this.setStatus(idx, ok ? 'ok' : 'failed');
      this.sending = false;
    } catch (e) { }
  }

  /** 打开链接：优先调起手机里的 B站/抖音 App，失败回退浏览器 */
  async openUrl(url: string) {
    const ctx = getContext(this) as common.UIAbilityContext;
    let uri = url;
    try {
      const m = url.match(/bilibili\.com\/video\/(BV[0-9A-Za-z]+)/);
      if (m) {
        uri = `bilibili://video/${m[1]}`;
      } else if (url.indexOf('douyin.com') >= 0) {
        uri = `snssdk1128://webview?url=${encodeURIComponent(url)}`;
      }
      await ctx.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        entities: ['entity.system.browsable'],
      });
    } catch (e) {
      try {
        await ctx.startAbility({
          action: 'ohos.want.action.viewData',
          uri: url,
          entities: ['entity.system.browsable'],
        });
      } catch (e2) { }
    }
  }

  /** 失败重试 */
  async retrySend(idx: number) {
    if (this.sending) return;
    if (idx < 0 || idx >= this.messages.length) return;
    const m = this.messages[idx];
    if (m.role !== 'user') return;
    this.setStatus(idx, 'sending');
    this.sending = true;
    const text = m.text.startsWith('[img:') ? '[图片]' : m.text;
    const ok = await this.postChat(text);
    this.setStatus(idx, ok ? 'ok' : 'failed');
    this.sending = false;
  }

  async sendEmoji(file: string) {
    if (this.sending) return;
    this.showEmoji = false;
    this.addMsg('user', `[img:${file}]`);
    this.sending = true;
    await this.postChat('[表情]');
    this.sending = false;
  }

  build() {
    Stack() {
      Column() {
        TopBar({
          name: this.herName,
          online: this.online,
          mood: this.mood,
          life: this.life,
          onBack: () => { router.back(); },
          onSettings: () => { router.pushUrl({ url: 'pages/Settings' }); },
          onStar: () => { router.pushUrl({ url: 'pages/StarMap' }); },
        })

        Divider().color('#1a2136').strokeWidth(0.5)

        MessageList({
          messages: this.messages,
          sending: this.sending,
          bgKey: this.bgKey,
          bgFrom: this.bgFrom(),
          bgTo: this.bgTo(),
          bgImage: this.bgImage,
          myAvatar: this.myAvatar,
          herAvatar: this.herAvatar,
          theme: this.theme,
          herName: this.herName,
          onQuick: (t: string) => { this.sendText(t); },
          onResend: (t: string) => { this.draft = t; },
          onDelete: (i: number) => { this.removeAt(i); },
          onRetry: (i: number) => { this.retrySend(i); },
          onOpenLink: (url: string) => { this.openUrl(url); },
        })
          .layoutWeight(1)

        if (this.showEmoji) {
          EmojiPanel({
            customEmojis: this.customEmojis,
            onPick: (e: string) => { this.draft = this.draft + e; },
            onPickImage: (f: string) => { this.sendEmoji(f); },
          })
        }

        ChatInput({
          sending: $sending,
          draft: this.draft,
          onSend: (t: string) => { this.sendText(t); },
          onToggleEmoji: () => { this.showEmoji = !this.showEmoji; },
          onPickImage: () => { this.pickImageAndSend(); },
          onFocusInput: () => { this.showEmoji = false; },
        })
      }
      .width('100%')
      .height('100%')
      .backgroundColor('#0d1017')

      if (this.showSplash) {
        Column() {
          Image($r('app.media.startIcon'))
            .width(132).height(132)
            .opacity(this.logoOpacity)
            .scale({ x: this.logoScale, y: this.logoScale })
          Text('安诗鱼')
            .fontSize(24).fontWeight(FontWeight.Medium).fontColor('#eef2ff')
            .opacity(this.titleOpacity)
            .offset({ y: this.titleOffset })
            .margin({ top: 20 })
          Text('她有自己的生活，也会想你')
            .fontSize(13).fontColor('#66739d')
            .opacity(this.titleOpacity)
            .offset({ y: this.titleOffset })
            .margin({ top: 10 })
        }
        .width('100%').height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#0d1017')
        .opacity(this.splashOpacity)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
