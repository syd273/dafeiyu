from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

s = s.replace("import { ChatStore, StoredMsg } from '../common/ChatStore';",
"""import { ChatStore, StoredMsg } from '../common/ChatStore';
import { Notifier } from '../common/Notifier';""")

# 页面可见状态
s = s.replace("  private lastAssistantTs: number = 0;",
"""  private lastAssistantTs: number = 0;
  private pageVisible: boolean = true;""")

# 启动时请求通知授权
s = s.replace("""    this.loadHistory();
    this.loadConfig().then(() => {""",
"""    Notifier.ensure(getContext(this) as Context);
    this.loadHistory();
    this.loadConfig().then(() => {""")

# 前后台
s = s.replace("""  onPageShow() {
    this.loadConfig().then(() => { this.loadStatus(); });
  }""",
"""  onPageShow() {
    this.pageVisible = true;
    this.loadConfig().then(() => { this.loadStatus(); });
  }

  onPageHide() {
    this.pageVisible = false;
  }""")

# WS 消息：后台时发通知
s = s.replace("""          if (m.type === 'message' && m.role === 'assistant' && m.text) {
            this.addMsg('assistant', m.text);
          }""",
"""          if (m.type === 'message' && m.role === 'assistant' && m.text) {
            this.addMsg('assistant', m.text);
            if (!this.pageVisible) {
              Notifier.notify('安诗鱼', m.text);
            }
          }""")

p.write_text(s, encoding="utf-8")
print("notifier wired")