// 配置读写工具：服务器地址（本地/云端）、头像、名字、主题、背景、自定义表情包
import preferences from '@ohos.data.preferences';
import fs from '@ohos.file.fs';
import { photoAccessHelper } from '@kit.MediaLibraryKit';

const STORE = 'anshiyu_config';
const KEY_BASE = 'base_url';
const KEY_LOCAL = 'local_url';
const KEY_CLOUD = 'cloud_url';
const KEY_MODE = 'server_mode';   // local | cloud
const KEY_NAME = 'her_name';
const KEY_MY_AVATAR = 'my_avatar';
const KEY_HER_AVATAR = 'her_avatar';
const KEY_EMOJIS = 'custom_emojis';
const KEY_THEME = 'theme_color';
const KEY_BG = 'chat_bg';
const KEY_BG_IMAGE = 'chat_bg_image';
const KEY_TOKEN = 'api_token';

export interface EmojiItem {
  name: string;
  file: string;
}

export class AppConfig {
  static async _pref(ctx: Context): Promise<preferences.Preferences> {
    return await preferences.getPreferences(ctx, STORE);
  }

  // ===== 服务器 =====
  static async getBase(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      const mode = (await p.get(KEY_MODE, 'local')) as string;
      if (mode === 'cloud') {
        const cloud = (await p.get(KEY_CLOUD, '')) as string;
        if (cloud) return cloud;
      }
      const local = (await p.get(KEY_LOCAL, '')) as string;
      if (local) return local;
      return (await p.get(KEY_BASE, 'http://192.168.43.5:8900')) as string;
    } catch (e) {
      return 'http://192.168.43.5:8900';
    }
  }

  static async getMode(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_MODE, 'local')) as string;
    } catch (e) {
      return 'local';
    }
  }

  static async setMode(ctx: Context, mode: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_MODE, mode);
    await p.flush();
  }

  static async getLocal(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      const v = (await p.get(KEY_LOCAL, '')) as string;
      if (v) return v;
      return (await p.get(KEY_BASE, 'http://192.168.43.5:8900')) as string;
    } catch (e) {
      return 'http://192.168.43.5:8900';
    }
  }

  static async setLocal(ctx: Context, url: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_LOCAL, url.trim());
    await p.put(KEY_BASE, url.trim());
    await p.flush();
  }

  static async getCloud(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_CLOUD, '')) as string;
    } catch (e) {
      return '';
    }
  }

  static async setCloud(ctx: Context, url: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_CLOUD, url.trim());
    await p.flush();
  }

  // ===== 连接令牌 =====
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

  // ===== 名字 =====
  static async getName(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_NAME, '安诗鱼')) as string;
    } catch (e) {
      return '安诗鱼';
    }
  }

  static async setName(ctx: Context, name: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_NAME, name.trim());
    await p.flush();
  }

  // ===== 头像 =====
  static async getAvatar(ctx: Context, who: string): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      const key = who === 'me' ? KEY_MY_AVATAR : KEY_HER_AVATAR;
      return (await p.get(key, '')) as string;
    } catch (e) {
      return '';
    }
  }

  static async pickAvatar(ctx: Context, who: string): Promise<string> {
    const picker = new photoAccessHelper.PhotoViewPicker();
    const opts: photoAccessHelper.PhotoSelectOptions = {
      MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE,
      maxSelectNumber: 1,
    };
    const res = await picker.select(opts);
    if (!res.photoUris || res.photoUris.length === 0) return '';
    const name = who === 'me' ? 'my_avatar.png' : 'her_avatar.png';
    const dst = `${ctx.filesDir}/${name}`;
    try { fs.unlinkSync(dst); } catch (e) { }
    const inFile = fs.openSync(res.photoUris[0], fs.OpenMode.READ_ONLY);
    const outFile = fs.openSync(dst, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
    fs.copyFileSync(inFile.fd, outFile.fd);
    fs.closeSync(inFile);
    fs.closeSync(outFile);
    const key = who === 'me' ? KEY_MY_AVATAR : KEY_HER_AVATAR;
    const p = await AppConfig._pref(ctx);
    await p.put(key, dst);
    await p.flush();
    return dst;
  }

  // ===== 主题 =====
  static async getTheme(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_THEME, '#3b6ef5')) as string;
    } catch (e) {
      return '#3b6ef5';
    }
  }

  static async setTheme(ctx: Context, color: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_THEME, color);
    await p.flush();
  }

  // ===== 背景 =====
  static async getBg(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_BG, 'default')) as string;
    } catch (e) {
      return 'default';
    }
  }

  static async setBg(ctx: Context, key: string): Promise<void> {
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_BG, key);
    await p.flush();
  }

  static async getBgImage(ctx: Context): Promise<string> {
    try {
      const p = await AppConfig._pref(ctx);
      return (await p.get(KEY_BG_IMAGE, '')) as string;
    } catch (e) {
      return '';
    }
  }

  static async pickBgImage(ctx: Context): Promise<string> {
    const picker = new photoAccessHelper.PhotoViewPicker();
    const opts: photoAccessHelper.PhotoSelectOptions = {
      MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE,
      maxSelectNumber: 1,
    };
    const res = await picker.select(opts);
    if (!res.photoUris || res.photoUris.length === 0) return '';
    const dst = `${ctx.filesDir}/chat_bg.png`;
    try { fs.unlinkSync(dst); } catch (e) { }
    const inFile = fs.openSync(res.photoUris[0], fs.OpenMode.READ_ONLY);
    const outFile = fs.openSync(dst, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
    fs.copyFileSync(inFile.fd, outFile.fd);
    fs.closeSync(inFile);
    fs.closeSync(outFile);
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_BG_IMAGE, dst);
    await p.put(KEY_BG, 'custom');
    await p.flush();
    return dst;
  }

  // ===== 表情包 =====
  static async getEmojis(ctx: Context): Promise<EmojiItem[]> {
    try {
      const p = await AppConfig._pref(ctx);
      const raw = (await p.get(KEY_EMOJIS, '[]')) as string;
      return JSON.parse(raw) as EmojiItem[];
    } catch (e) {
      return [];
    }
  }

  static async addEmojis(ctx: Context, max: number = 9): Promise<EmojiItem[]> {
    const picker = new photoAccessHelper.PhotoViewPicker();
    const opts: photoAccessHelper.PhotoSelectOptions = {
      MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE,
      maxSelectNumber: max,
    };
    const res = await picker.select(opts);
    const list = await AppConfig.getEmojis(ctx);
    if (!res.photoUris) return list;
    const dir = `${ctx.filesDir}/emojis`;
    try { fs.mkdirSync(dir); } catch (e) { }
    let n = 0;
    for (const uri of res.photoUris) {
      const file = `${dir}/emoji_${Date.now()}_${n}.png`;
      try {
        const inFile = fs.openSync(uri, fs.OpenMode.READ_ONLY);
        const outFile = fs.openSync(file, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE);
        fs.copyFileSync(inFile.fd, outFile.fd);
        fs.closeSync(inFile);
        fs.closeSync(outFile);
        list.push({ name: `表情${list.length + 1}`, file });
        n++;
      } catch (e) { }
    }
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_EMOJIS, JSON.stringify(list));
    await p.flush();
    return list;
  }

  static async removeEmoji(ctx: Context, file: string): Promise<EmojiItem[]> {
    const list = await AppConfig.getEmojis(ctx);
    const rest = list.filter((x: EmojiItem) => x.file !== file);
    try { fs.unlinkSync(file); } catch (e) { }
    const p = await AppConfig._pref(ctx);
    await p.put(KEY_EMOJIS, JSON.stringify(rest));
    await p.flush();
    return rest;
  }
}
