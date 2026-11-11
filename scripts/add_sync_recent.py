from pathlib import Path

# 1) ChatStore 加 lastSync
p = Path(r"D:\anshiyu_app\entry\src\main\ets\common\ChatStore.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("const KEY_MSGS = 'messages';",
"""const KEY_MSGS = 'messages';
const KEY_SYNC = 'last_sync';""")
s += """

export class SyncState {
  static async get(ctx: Context): Promise<number> {
    try {
      const p = await preferences.getPreferences(ctx, STORE);
      return (await p.get(KEY_SYNC, 0)) as number;
    } catch (e) {
      return 0;
    }
  }

  static async set(ctx: Context, ts: number): Promise<void> {
    try {
      const p = await preferences.getPreferences(ctx, STORE);
      await p.put(KEY_SYNC, ts);
      await p.flush();
    } catch (e) { }
  }
}
"""
p.write_text(s, encoding="utf-8")
print("ChatStore lastSync 已加")

# 2) Index 启动同步
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { ChatStore, StoredMsg } from '../common/ChatStore';",
              "import { ChatStore, StoredMsg, SyncState } from '../common/ChatStore';")
s = s.replace("""    Notifier.ensure(getContext(this) as common.UIAbilityContext);
    this.loadHistory();""",
"""    Notifier.ensure(getContext(this) as common.UIAbilityContext);
    this.loadHistory();
    this.syncRecent();""")
s = s.replace("""  async loadHistory() {""",
"""  /** 打开 App 时同步她之前发过的主动消息（离线补消息） */
  async syncRecent() {
    try {
      const ctx = getContext(this) as Context;
      const since = await SyncState.get(ctx);
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/messages/recent?token=${TOKEN}&since=${since}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 10000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const items = (d.items ?? []) as Array<Record<string, Object>>;
        for (const it of items) {
          const text = (it.text ?? '') as string;
          if (!text) continue;
          this.addMsg('assistant', text);
        }
        await SyncState.set(ctx, Math.floor(Date.now() / 1000));
      }
    } catch (e) { }
  }

  async loadHistory() {""")
p.write_text(s, encoding="utf-8")
print("Index 离线同步已加")