from pathlib import Path

# ===== 1) ChatInput：加图片按钮 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\ChatInput.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  onToggleEmoji: () => void = () => { };",
"""  onToggleEmoji: () => void = () => { };
  onPickImage: () => void = () => { };""")
s = s.replace("""      Text('😊')
        .fontSize(23).width(40).height(40).textAlign(TextAlign.Center)
        .backgroundColor('#161b29').borderRadius(20)
        .onClick(() => { this.onToggleEmoji(); })""",
"""      Text('＋')
        .fontSize(20).width(36).height(36).textAlign(TextAlign.Center)
        .fontColor('#bcd0ff').backgroundColor('#161b29').borderRadius(18)
        .onClick(() => { this.onPickImage(); })
      Text('😊')
        .fontSize(23).width(40).height(40).textAlign(TextAlign.Center)
        .backgroundColor('#161b29').borderRadius(20)
        .margin({ left: 6 })
        .onClick(() => { this.onToggleEmoji(); })""")
p.write_text(s, encoding="utf-8")
print("ChatInput 图片按钮已加")

# ===== 2) MessageList：ChatMsg 加 status + 失败重试 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\MessageList.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""export interface ChatMsg {
  role: string;   // user / assistant
  text: string;
  ts: number;
}""",
"""export interface ChatMsg {
  role: string;   // user / assistant
  text: string;
  ts: number;
  status?: string;  // sending / ok / failed
}""")
s = s.replace("  onDelete: (i: number) => void = () => { };",
"""  onDelete: (i: number) => void = () => { };
  onRetry: (i: number) => void = () => { };""")

# 用户气泡下方加状态行
s = s.replace("""        if (this.myAvatar) {
          Image('file://' + this.myAvatar)
            .width(32).height(32).borderRadius(16).margin({ left: 8, top: 2 })
        } else {
          Text('东')
            .width(32).height(32).fontSize(12).fontColor('#cfe0ff')
            .textAlign(TextAlign.Center).backgroundColor('#25324f').borderRadius(16)
            .margin({ left: 8, top: 2 })
        }""",
"""        Column() {
          if (this.myAvatar) {
            Image('file://' + this.myAvatar)
              .width(32).height(32).borderRadius(16)
          } else {
            Text('东')
              .width(32).height(32).fontSize(12).fontColor('#cfe0ff')
              .textAlign(TextAlign.Center).backgroundColor('#25324f').borderRadius(16)
          }
          if (m.status === 'sending') {
            Text('发送中').fontSize(9).fontColor('#8fa2d8').margin({ top: 2 })
          } else if (m.status === 'failed') {
            Text('失败·重试').fontSize(9).fontColor('#ff6b6b').margin({ top: 2 })
              .onClick(() => { this.onRetry(idx); })
          }
        }
        .alignItems(HorizontalAlign.Center)
        .margin({ left: 8, top: 2 })""")
p.write_text(s, encoding="utf-8")
print("MessageList 状态与重试已加")

# ===== 3) Index：图片发送 + 状态维护 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { ChatStore, StoredMsg } from '../common/ChatStore';",
"""import { ChatStore, StoredMsg } from '../common/ChatStore';
import { photoAccessHelper } from '@kit.MediaLibraryKit';
import fs from '@ohos.file.fs';""")

# addMsg 带状态
s = s.replace("""  addMsg(role: string, text: string) {
    if (role === 'assistant') {
      const now = Date.now();
      if (text === this.lastAssistant && now - this.lastAssistantTs < 3000) return;
      this.lastAssistant = text;
      this.lastAssistantTs = now;
    }
    this.messages = this.messages.concat([{ role: role, text: text, ts: Date.now() }]);
    this.saveHistory();
  }""",
"""  addMsg(role: string, text: string, status: string = 'ok') {
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
  }""")

# sendText 维护状态
s = s.replace("""  async sendText(t: string) {
    const text = t.trim();
    if (!text || this.sending) return;
    this.showEmoji = false;
    this.addMsg('user', text);
    this.sending = true;
    await this.postChat(text);
    this.sending = false;
  }""",
"""  async sendText(t: string) {
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
  }""")

# postChat 返回布尔
s = s.replace("""  async postChat(t: string) {
    try {""",
"""  async postChat(t: string): Promise<boolean> {
    try {""")
s = s.replace("""      if (d.life) {
        const lifeObj = d.life as Record<string, string>;
        this.mood = (d.mood ?? '平静') as string;
        this.life = `${lifeObj.location ?? ''} ${lifeObj.activity ?? ''}`;
      }
    } catch (e) {
      this.addMsg('assistant', '（连接失败，请检查设置里的服务器地址和电脑端网关）');
    }
  }""",
"""      if (d.life) {
        const lifeObj = d.life as Record<string, string>;
        this.mood = (d.mood ?? '平静') as string;
        this.life = `${lifeObj.location ?? ''} ${lifeObj.activity ?? ''}`;
      }
      return true;
    } catch (e) {
      this.addMsg('assistant', '（连接失败，请检查设置里的服务器地址或网络）');
      return false;
    }
  }""")

# ChatInput 传 onPickImage；MessageList 传 onRetry
s = s.replace("""          onQuick: (t: string) => { this.sendText(t); },
          onResend: (t: string) => { this.draft = t; },
          onDelete: (i: number) => { this.removeAt(i); },""",
"""          onQuick: (t: string) => { this.sendText(t); },
          onResend: (t: string) => { this.draft = t; },
          onDelete: (i: number) => { this.removeAt(i); },
          onRetry: (i: number) => { this.retrySend(i); },""")
s = s.replace("""          onSend: (t: string) => { this.sendText(t); },
          onToggleEmoji: () => { this.showEmoji = !this.showEmoji; },
          onFocusInput: () => { this.showEmoji = false; },""",
"""          onSend: (t: string) => { this.sendText(t); },
          onToggleEmoji: () => { this.showEmoji = !this.showEmoji; },
          onPickImage: () => { this.pickImageAndSend(); },
          onFocusInput: () => { this.showEmoji = false; },""")
p.write_text(s, encoding="utf-8")
print("Index 图片与状态已加")