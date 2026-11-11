// 她的说说（像朋友圈/空间动态）
import http from '@ohos.net.http';
import router from '@ohos.router';
import { AppConfig } from '../common/Config';
import { Notifier } from '../common/Notifier';
import { common } from '@kit.AbilityKit';

const TOKEN = 'anshiyu-app-2026';

interface SayItem {
  text: string;
  mood: string;
  kind: string;
  ts: number;
}

@Entry
@Component
struct Says {
  @State baseUrl: string = '';
  @State items: SayItem[] = [];
  @State loading: boolean = false;
  @State tip: string = '';

  aboutToAppear() {
    this.init();
  }

  async init() {
    const ctx = getContext(this) as Context;
    this.baseUrl = await AppConfig.getBase(ctx);
    await this.load();
  }

  async load() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/says?token=${TOKEN}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.items = ((d.items ?? []) as SayItem[]);
      }
    } catch (e) { }
  }

  fmt(ts: number): string {
    if (!ts) return '';
    const d = new Date(ts * 1000);
    const mm = (d.getMonth() + 1).toString().padStart(2, '0');
    const dd = d.getDate().toString().padStart(2, '0');
    const hh = d.getHours().toString().padStart(2, '0');
    const mi = d.getMinutes().toString().padStart(2, '0');
    return `${mm}-${dd} ${hh}:${mi}`;
  }

  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('她的说说').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text('💬').fontSize(18)
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      Scroll() {
        Column() {
          if (this.tip) {
            Text(this.tip).fontSize(11).fontColor('#ffd48a').width('100%').margin({ top: 8 })
          }

          Text('她会自己发说说，你可以在设置里调她的说说频率')
            .fontSize(11).fontColor('#5f6c96').width('100%').margin({ top: 10 })

          if (this.items.length === 0) {
            Text('她还没发过说说').fontSize(12).fontColor('#5f6c96').margin({ top: 30 })
          } else {
            ForEach(this.items, (it: SayItem) => {
              Column() {
                Row() {
                  Text(it.mood || '平静').fontSize(10).fontColor('#ffd48a')
                    .padding({ left: 8, right: 8, top: 2, bottom: 2 })
                    .backgroundColor('#2a2440').borderRadius(8)
                  Blank()
                  Text(this.fmt(it.ts)).fontSize(10).fontColor('#5f6c96')
                }
                .width('100%')
                Text(it.text)
                  .fontSize(14).lineHeight(21).fontColor('#e8eeff')
                  .margin({ top: 8 }).width('100%')
              }
              .width('100%').padding(14)
              .backgroundColor('#121826').borderRadius(14).margin({ top: 10 })
            }, (it: SayItem) => `${it.ts}_${it.text.length}`)
          }
        }
        .padding({ left: 16, right: 16, bottom: 30 })
      }
      .edgeEffect(EdgeEffect.Spring)
      .layoutWeight(1)
    }
    .padding({ top: 38 })
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
