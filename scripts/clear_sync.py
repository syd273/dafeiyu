from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { ChatStore } from '../common/ChatStore';",
              "import { ChatStore, SyncState } from '../common/ChatStore';")
s = s.replace("""    await ChatStore.clear(ctx);""",
"""    await ChatStore.clear(ctx);
    // 防止重启 App 时把旧主动消息补收回来
    await SyncState.set(ctx, Math.floor(Date.now() / 1000));""")
p.write_text(s, encoding="utf-8")
print("同步游标重置已加")