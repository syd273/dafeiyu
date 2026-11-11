// 生活记录页：她的动态 + 生活事件 + 日记（时间线）
import http from '@ohos.net.http';
import router from '@ohos.router';
import { AppConfig } from '../common/Config';

const TOKEN = 'anshiyu-app-2026';

interface LogItem {
  ts: number;
  kind: string;   // talk/share/proactive/diary/event
  text: string;
}

@Entry
@Component
struct LifeLog {
  @State items: LogItem[] = [];
  @State loading: boolean = true;
  @State baseUrl: string = '';
  private name: string = '安诗鱼';

  aboutToAppear() {
    this.load();
  }

  async load() {
    const ctx = getContext(this) as Context;
    this.baseUrl = await AppConfig.getBase(ctx);
    this.name = await AppConfig.getName(ctx);
    const out: LogItem[] = [];
    // 她的动态（说说/分享/主动/日记）
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/feed?token=${TOKEN}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const items = (d.items ?? []) as Array<Record<string, Object>>;
        for (const it of items) {
          out.push({
            ts: (it.ts as number) * 1000,
            kind: (it.kind ?? 'talk') as string,
            text: (it.text ?? '') as string,
          });
        }
      }
    } catch (e) { }
    // 生活事件
    try {
      const req2 = http.createHttp();
      const res2 = await req2.request(`${this.baseUrl}/api/memories?token=${TOKEN}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req2.destroy();
      if (res2.responseCode === 200) {
        const d2 = JSON.parse(res2.result as string) as Record<string, Object>;
        const eps = (d2.episodes ?? []) as Array<Record<string, Object>>;
        for (const e of eps) {
          out.push({
            ts: (e.ts as number) * 1000,
            kind: 'event',
            text: (e.text ?? '') as string,
          });
        }
      }
    } catch (e) { }

    out.sort((a: LogItem, b: LogItem) => b.ts - a.ts);
    this.items = out.slice(0, 200);
    this.loading = false;
  }

  fmt(ts: number): string {
    const d = new Date(ts);
    const p = (n: number): string => n < 10 ? '0' + n : '' + n;
    return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`;
  }

  kindLabel(kind: string): string {
    if (kind === 'share') return '分享';
    if (kind === 'proactive') return '主动';
    if (kind === 'diary') return '日记';
    if (kind === 'event') return '生活';
    return '说说';
  }

  kindColor(kind: string): string {
    if (kind === 'share') return '#c39bff';
    if (kind === 'proactive') return '#ffc98a';
    if (kind === 'diary') return '#9fe0b8';
    if (kind === 'event') return '#8fb3ff';
    return '#9db4ef';
  }

  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('生活记录').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text(this.loading ? '加载中…' : `${this.items.length} 条`)
          .fontSize(12).fontColor('#5f6c96')
          .onClick(() => { this.load(); })
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      Divider().color('#1a2136').strokeWidth(0.5)

      if (this.loading) {
        Column() {
          LoadingProgress().width(36).height(36).color('#5f6c96')
        }
        .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else if (this.items.length === 0) {
        Column() {
          Text('还没有生活记录').fontSize(13).fontColor('#5f6c96')
        }
        .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else {
        List() {
          ForEach(this.items, (it: LogItem) => {
            ListItem() {
              Row() {
                Text(this.fmt(it.ts))
                  .fontSize(11).fontColor('#5d6a92').width(86)
                Column() {
                  Row() {
                    Text(this.kindLabel(it.kind))
                      .fontSize(10).fontColor(this.kindColor(it.kind))
                      .padding({ left: 6, right: 6, top: 1, bottom: 1 })
                      .backgroundColor('#1a2138')
                      .borderRadius(8)
                  }
                  .margin({ bottom: 4 })
                  Text(it.text)
                    .fontSize(14).fontColor('#dbe4ff').lineHeight(20)
                }
                .alignItems(HorizontalAlign.Start)
                .layoutWeight(1)
              }
              .width('100%')
              .alignItems(VerticalAlign.Top)
              .padding({ top: 8, bottom: 8 })
            }
          }, (it: LogItem) => `${it.ts}_${it.kind}_${it.text.slice(0, 10)}`)
        }
        .width('100%')
        .layoutWeight(1)
        .padding({ left: 14, right: 14 })
        .divider({ strokeWidth: 0.5, color: '#151b2b' })
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
