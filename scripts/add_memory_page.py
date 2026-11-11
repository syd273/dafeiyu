import json
from pathlib import Path

# 路由
p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
if "pages/MemoryRecords" not in d["src"]:
    d["src"].append("pages/MemoryRecords")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("路由:", d["src"])

# 设置页"更多"加记忆记录按钮
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""              Button('生活记录')
                .height(36).layoutWeight(1).margin({ left: 10 })
                .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
                .borderRadius(12)
                .onClick(() => { router.pushUrl({ url: 'pages/LifeLog' }); })""",
"""              Button('生活记录')
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
            Row() {""")
p.write_text(s, encoding="utf-8")
print("设置页入口已加")