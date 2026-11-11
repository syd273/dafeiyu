import json
from pathlib import Path

p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
if "pages/Legacy" not in d["src"]:
    d["src"].append("pages/Legacy")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("路由:", d["src"])

p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""            Button('🎧 一起听歌')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Music' }); })""",
"""            Button('🎧 一起听歌')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Music' }); })
            Button('🕯️ 她的传承')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Legacy' }); })""")
p.write_text(s, encoding="utf-8")
print("设置入口已加")