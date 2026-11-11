// 聊天记录本地存储（重启不丢）
import preferences from '@ohos.data.preferences';

export interface StoredMsg {
  role: string;
  text: string;
  ts: number;
}

const STORE = 'anshiyu_chat';
const KEY_MSGS = 'messages';
const KEY_SYNC = 'last_sync';
const MAX_KEEP = 300;

export class ChatStore {
  private static saveTimer: number = -1;

  static async load(ctx: Context): Promise<StoredMsg[]> {
    try {
      const p = await preferences.getPreferences(ctx, STORE);
      const raw = (await p.get(KEY_MSGS, '[]')) as string;
      return JSON.parse(raw) as StoredMsg[];
    } catch (e) {
      return [];
    }
  }

  /** 防抖保存，避免每条消息都写盘 */
  static save(ctx: Context, msgs: StoredMsg[]): void {
    if (ChatStore.saveTimer >= 0) {
      clearTimeout(ChatStore.saveTimer);
    }
    ChatStore.saveTimer = setTimeout(async () => {
      try {
        const p = await preferences.getPreferences(ctx, STORE);
        const keep = msgs.slice(-MAX_KEEP);
        await p.put(KEY_MSGS, JSON.stringify(keep));
        await p.flush();
      } catch (e) { }
    }, 400);
  }

  static async clear(ctx: Context): Promise<void> {
    try {
      const p = await preferences.getPreferences(ctx, STORE);
      await p.delete(KEY_MSGS);
      await p.flush();
    } catch (e) { }
  }
}


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
