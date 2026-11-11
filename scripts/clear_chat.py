from pathlib import Path

# 1) Settings：清空聊天记录按钮（保留记忆）
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { Notifier } from '../common/Notifier';",
"""import { Notifier } from '../common/Notifier';
import { ChatStore } from '../common/ChatStore';""")

# 清空方法（加在 saveName 前）
s = s.replace("""  async saveName() {""",
"""  async clearChat() {
    const ctx = getContext(this) as Context;
    await ChatStore.clear(ctx);
    // 重置离线同步游标，保持消息与服务器一致
    this.tip = '聊天记录已清空（她的记忆和星图都还在）';
  }

  async saveName() {""")

# 卡片（放在"更多"前面）
s = s.replace("""          // 她的内容来源""",
"""          // 聊天记录
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

          // 她的内容来源""")
p.write_text(s, encoding="utf-8")
print("设置页清空按钮已加")

# 2) Index：onPageShow 重新加载历史（空则清空界面）
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""  onPageShow() {
    this.pageVisible = true;
    this.loadConfig().then(() => { this.loadStatus(); });
  }""",
"""  onPageShow() {
    this.pageVisible = true;
    this.loadConfig().then(() => {
      this.loadStatus();
      // 从设置页返回时重新加载聊天记录（支持清空）
      this.loadHistory();
    });
  }""")
s = s.replace("""      const list = await ChatStore.load(ctx);
      if (list && list.length > 0) {
        this.messages = list;
      }""",
"""      const list = await ChatStore.load(ctx);
      this.messages = list && list.length > 0 ? list : [];""")
p.write_text(s, encoding="utf-8")
print("Index 历史重载已加")