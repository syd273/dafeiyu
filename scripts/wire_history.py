from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

s = s.replace("import { MessageList, ChatMsg } from '../components/MessageList';",
"""import { MessageList, ChatMsg } from '../components/MessageList';
import { ChatStore, StoredMsg } from '../common/ChatStore';""")

# 启动时加载历史
s = s.replace("""    this.splashStart = Date.now();
    this.startSplash();
    this.loadConfig().then(() => {""",
"""    this.splashStart = Date.now();
    this.startSplash();
    this.loadHistory();
    this.loadConfig().then(() => {""")

# 历史加载方法
s = s.replace("""  startSplash() {""",
"""  async loadHistory() {
    try {
      const ctx = getContext(this) as Context;
      const list = await ChatStore.load(ctx);
      if (list && list.length > 0) {
        this.messages = list;
      }
    } catch (e) { }
  }

  startSplash() {""")

# addMsg：保存
s = s.replace("""    this.messages = this.messages.concat([{ role: role, text: text, ts: Date.now() }]);
  }""",
"""    this.messages = this.messages.concat([{ role: role, text: text, ts: Date.now() }]);
    this.saveHistory();
  }

  saveHistory() {
    const ctx = getContext(this) as Context;
    ChatStore.save(ctx, this.messages as StoredMsg[]);
  }""")

# 删除后保存
s = s.replace("""      arr.splice(idx, 1);
      this.messages = arr;
    }""",
"""      arr.splice(idx, 1);
      this.messages = arr;
      this.saveHistory();
    }""")

p.write_text(s, encoding="utf-8")
print("history persistence wired")