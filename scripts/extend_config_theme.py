from pathlib import Path

# ===== Config.ets：主题色 / 聊天背景 =====
p = Path(r"D:\anshiyu_app\entry\src\main\ets\common\Config.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("const KEY_EMOJIS = 'custom_emojis';",
"""const KEY_EMOJIS = 'custom_emojis';
const KEY_THEME = 'theme_color';
const KEY_BG = 'chat_bg';
const KEY_BG_IMAGE = 'chat_bg_image';""")
s = s.replace("""  static async getEmojis(ctx: Context): Promise<EmojiItem[]> {""",
"""  // ===== 主题色 =====
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

  // ===== 聊天背景 =====
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

  /** 从相册选聊天背景图 */
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

  static async getEmojis(ctx: Context): Promise<EmojiItem[]> {""")
p.write_text(s, encoding="utf-8")
print("Config extended")