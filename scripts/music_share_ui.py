from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Music.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State baseUrl: string = '';",
              "  @State baseUrl: string = '';\n  @State shareText: string = '';")

# 分享方法
s = s.replace("  async openSong() {",
"""  async share() {
    const t = this.shareText.trim();
    if (!t) return;
    this.loading = true;
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/music/share?token=${TOKEN}`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ text: t }),
        connectTimeout: 10000, readTimeout: 60000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        this.song = d.song as Song;
        this.text = (d.text ?? '') as string;
        this.shareText = '';
      } else {
        this.text = (d.error ?? '分享失败') as string;
      }
    } catch (e) {
      this.text = '分享失败，检查网络或链接';
    }
    this.loading = false;
  }

  async openSong() {""")

# UI：顶部加分享输入
s = s.replace("""      Scroll() {
        Column() {
          if (this.song) {""",
"""      Scroll() {
        Column() {
          // 分享一首歌给她
          Row() {
            TextInput({ text: this.shareText, placeholder: '粘贴 B站 视频链接，分享给她' })
              .layoutWeight(1)
              .fontSize(13).fontColor('#e8eeff').placeholderColor('#5f6c96')
              .backgroundColor('#161b29').borderRadius(12)
              .onChange((v: string) => { this.shareText = v; })
            Button('分享')
              .height(36).width(56).margin({ left: 8 })
              .backgroundColor('#3b6ef5').fontSize(13).fontColor('#ffffff')
              .borderRadius(18)
              .enabled(!this.loading && this.shareText.trim().length > 0)
              .onClick(() => { this.share(); })
          }
          .width('100%')
          .margin({ top: 12 })

          if (this.song) {""")
p.write_text(s, encoding="utf-8")
print("Music 分享输入已加")