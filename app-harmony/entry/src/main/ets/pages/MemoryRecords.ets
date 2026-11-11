// 记忆记录（本地缓存 + 星序排列 + 搜索 + 删除）
import http from '@ohos.net.http';
import router from '@ohos.router';
import preferences from '@ohos.data.preferences';
import { AppConfig } from '../common/Config';

const TOKEN = 'anshiyu-app-2026';
const STORE = 'anshiyu_memory';
const KEY_MEMS = 'memory_records';

interface MemItem {
  id: number;
  index: number;
  ts: number;
  text: string;
  emo: string;
  speaker: string;
}

@Entry
@Component
struct MemoryRecords {
  @State allItems: MemItem[] = [];
  @State query: string = '';
  @State loading: boolean = false;
  @State total: number = 0;
  @State tip: string = '';
  @State fromCache: boolean = false;
  @State pendingDelete: number = -1;
  private baseUrl: string = '';

  aboutToAppear() {
    this.init();
  }

  async init() {
    const ctx = getContext(this) as Context;
    this.baseUrl = await AppConfig.getBase(ctx);
    // 先读手机本地缓存
    await this.loadCache();
    // 再拉服务端刷新
    await this.load();
  }

  async loadCache() {
    try {
      const ctx = getContext(this) as Context;
      const p = await preferences.getPreferences(ctx, STORE);
      const raw = (await p.get(KEY_MEMS, '[]')) as string;
      const list = JSON.parse(raw) as MemItem[];
      if (list.length > 0) {
        this.allItems = list;
        this.total = list.length;
        this.fromCache = true;
      }
    } catch (e) { }
  }

  async saveCache() {
    try {
      const ctx = getContext(this) as Context;
      const p = await preferences.getPreferences(ctx, STORE);
      await p.put(KEY_MEMS, JSON.stringify(this.allItems));
      await p.flush();
    } catch (e) { }
  }

  async load() {
    this.loading = true;
    try {
      const req = http.createHttp();
      const url = `${this.baseUrl}/api/memory/records?token=${TOKEN}&limit=1000`;
      const res = await req.request(url, { method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 15000 });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const items = (d.items ?? []) as MemItem[];
        // 按星序排列（后端已排序，这里再保证一次）
        items.sort((a: MemItem, b: MemItem) => a.index - b.index);
        this.allItems = items;
        this.total = items.length;
        this.fromCache = false;
        await this.saveCache();
      } else {
        this.tip = '服务器返回 ' + res.responseCode + '，显示本地缓存';
      }
    } catch (e) {
      this.tip = '离线：显示手机保存的记忆';
    }
    this.loading = false;
  }

  filtered(): MemItem[] {
    if (!this.query) return this.allItems;
    return this.allItems.filter((x: MemItem) => x.text.indexOf(this.query) >= 0);
  }

  fmt(ts: number): string {
    if (!ts) return '';
    const d = new Date(ts * 1000);
    const p = (n: number): string => n < 10 ? '0' + n : '' + n;
    return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }

  async remove(item: MemItem) {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/memory/delete?token=${TOKEN}`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ id: item.id }),
        connectTimeout: 8000,
        readTimeout: 15000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        this.tip = '已删除，剩余 ' + d.remaining + ' 颗星';
        await this.load();
      } else {
        this.tip = '删除失败：' + (d.error ?? '');
      }
    } catch (e) {
      this.tip = '删除失败（需要连接服务器）';
    }
  }

  build() {
    Column() {
      // 顶部
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('记忆记录').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text(this.loading ? '刷新中' : `${this.total} 颗星`)
          .fontSize(12).fontColor('#5f6c96')
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      // 搜索
      Row() {
        Text('🔍').fontSize(15).padding({ left: 12 })
        TextInput({ text: this.query, placeholder: '搜索关键词，如：阿东' })
          .layoutWeight(1)
          .fontSize(14).fontColor('#e8eeff').placeholderColor('#5f6c96')
          .backgroundColor('#00000000')
          .onChange((v: string) => { this.query = v; })
        if (this.query) {
          Text('✕').fontSize(14).fontColor('#6f7fae').padding({ right: 8 })
            .onClick(() => { this.query = ''; })
        }
      }
      .width('100%')
      .height(44)
      .margin({ left: 12, right: 12, top: 10 })
      .backgroundColor('#161b29')
      .borderRadius(14)

      if (this.tip) {
        Text(this.tip).fontSize(12).fontColor('#8fa2d8')
          .width('100%').padding({ left: 16, top: 8 })
      }
      if (this.fromCache) {
        Text('（离线显示手机保存的记忆）').fontSize(10).fontColor('#4a567c')
          .width('100%').padding({ left: 16, top: 2 })
      }

      if (this.filtered().length === 0) {
        Column() {
          Text(this.query ? '没有找到相关记忆' : '还没有记忆').fontSize(13).fontColor('#5f6c96')
        }
        .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else {
        List() {
          ForEach(this.filtered(), (it: MemItem) => {
            ListItem() {
              Column() {
                Row() {
                  Text(`⭐ 第 ${it.index} 颗星`)
                    .fontSize(10).fontColor('#ffd48a')
                    .padding({ left: 6, right: 6, top: 1, bottom: 1 })
                    .backgroundColor('#1a2138')
                    .borderRadius(8)
                  Text(`${it.emo} · ${this.fmt(it.ts)}`)
                    .fontSize(10).fontColor('#5d6a92').margin({ left: 8 })
                  Blank()
                  Text(this.pendingDelete === it.id ? '确认删除？' : '删除')
                    .fontSize(11)
                    .fontColor(this.pendingDelete === it.id ? '#ff3b3b' : '#ff6b6b')
                    .padding({ left: 8, right: 4, top: 2, bottom: 2 })
                    .onClick(() => {
                      if (this.pendingDelete === it.id) {
                        this.pendingDelete = -1;
                        this.remove(it);
                      } else {
                        this.pendingDelete = it.id;
                        this.tip = '再点一次「确认删除」才会删除';
                      }
                    })
                }
                .width('100%')
                Text(it.text)
                  .fontSize(14).fontColor('#dbe4ff').lineHeight(20)
                  .margin({ top: 6 })
                  .width('100%')
              }
              .width('100%')
              .alignItems(HorizontalAlign.Start)
              .padding({ top: 10, bottom: 10 })
            }
          }, (it: MemItem) => `${it.id}_${it.ts}`)
        }
        .width('100%')
        .layoutWeight(1)
        .padding({ left: 14, right: 14, top: 6 })
        .divider({ strokeWidth: 0.5, color: '#151b2b' })
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
