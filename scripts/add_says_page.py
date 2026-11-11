import json
from pathlib import Path

p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
if "pages/Says" not in d["src"]:
    d["src"].append("pages/Says")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("路由:", d["src"])

p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""            Button('🌅 上帝视角（看她的生活）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/GodView' }); })""",
"""            Button('🌅 上帝视角（看她的生活）')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/GodView' }); })
            Button('💬 她的说说')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Says' }); })""")
p.write_text(s, encoding="utf-8")
print("设置入口已加")

# Index 的 WS 收到 say 时通知
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""    this.ws.on('message', (err: Error, data: string | ArrayBuffer) => {""",
"""    this.ws.on('message', (err: Error, data: string | ArrayBuffer) => {
      try {
        const raw = typeof data === 'string' ? data : '';
        const msg = raw ? JSON.parse(raw) as Record<string, Object> : null;
        if (msg && msg.type === 'say' && msg.text) {
          Notifier.notify('安诗鱼 · 说说', msg.text as string);
          return;
        }
      } catch (e) { }""")
p.write_text(s, encoding="utf-8")
print("Index 说说通知已加")