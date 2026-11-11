from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { AppConfig, EmojiItem } from '../common/Config';",
"""import { AppConfig, EmojiItem } from '../common/Config';
import { Notifier } from '../common/Notifier';""")

# 在「服务器地址」卡片前加通知测试卡片
s = s.replace("""          // 服务器
          Column() {
            Text('🌐  服务器地址')""",
"""          // 通知测试
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

          // 服务器
          Column() {
            Text('🌐  服务器地址')""")
p.write_text(s, encoding="utf-8")
print("test notify button added")