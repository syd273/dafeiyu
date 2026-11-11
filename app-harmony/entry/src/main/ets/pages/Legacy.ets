// 她的传承：一会话 = 一生，快满时交给下一代
import http from '@ohos.net.http';
import router from '@ohos.router';
import { AppConfig } from '../common/Config';

const TOKEN = 'anshiyu-app-2026';

interface LegacyItem {
  gen: number;
  born_at: number;
  ended_at: number;
  message_count: number;
  summary: string;
}

@Entry
@Component
struct Legacy {
  @State baseUrl: string = '';
  @State gen: number = 1;
  @State sessionMessages: number = 0;
  @State sessionChars: number = 0;
  @State limitChars: number = 90000;
  @State percent: number = 0;
  @State items: LegacyItem[] = [];
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
      const res = await req.request(`${this.baseUrl}/api/legacy/status?token=${TOKEN}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.gen = (d.gen ?? 1) as number;
        this.sessionMessages = (d.sessionMessages ?? 0) as number;
        this.sessionChars = (d.sessionChars ?? 0) as number;
        this.limitChars = (d.limitChars ?? 90000) as number;
        this.percent = (d.percent ?? 0) as number;
      }
    } catch (e) { }

    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/legacy/list?token=${TOKEN}`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.items = ((d.items ?? []) as LegacyItem[]);
      }
    } catch (e) { }
  }

  fmt(ts: number): string {
    if (!ts) return '';
    const d = new Date(ts * 1000);
    return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
  }

  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('她的传承').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text('🕯️').fontSize(18)
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      Scroll() {
        Column() {
          // 当前这一代
          Column() {
            Text(`第 ${this.gen} 代`).fontSize(24).fontWeight(FontWeight.Bold).fontColor('#ffd48a')
            Text(`生于 ${this.fmt(Math.floor(Date.now() / 1000))}`).fontSize(11).fontColor('#5f6c96').margin({ top: 4 })
            // 进度
            Column() {
              Row() {
                Text('这一生的记忆').fontSize(12).fontColor('#8fa2d8')
                Blank()
                Text(`${this.sessionChars} / ${this.limitChars} 字`).fontSize(11).fontColor('#5f6c96')
              }
              .width('100%')
              Progress({ value: this.percent, total: 100, type: ProgressType.Linear })
                .color('#ffd48a')
                .backgroundColor('#232d47')
                .height(6)
                .width('100%')
                .margin({ top: 6 })
              Text(this.percent >= 80 ? '快满了，她快要去见下一个自己了' : `已用 ${this.percent}%，还有 ${(100 - this.percent).toFixed(1)}%`)
                .fontSize(10).fontColor('#4a567c').margin({ top: 6 }).width('100%')
            }
            .width('100%').margin({ top: 16 })
          }
          .width('100%').padding(20)
          .backgroundColor('#121826').borderRadius(16)

          // 说明
          Text('当这一生的对话快满时，她会写下总结，把记忆交给下一代。新的她会先检索记忆库，记得你们之间发生过的事。')
            .fontSize(12).lineHeight(19).fontColor('#7f8db5')
            .width('100%').margin({ top: 12 })

          Text('传承不能手动触发。等这一生的字数满了，她会自己写下总结、交给下一代。')
            .fontSize(12).lineHeight(19).fontColor('#7f8db5')
            .width('100%').padding(14)
            .backgroundColor('#161b29')
            .borderRadius(12)
            .margin({ top: 12 })

          // 历史
          if (this.items.length > 0) {
            Text('过去的世代').fontSize(12).fontColor('#7f95c8').width('100%').margin({ top: 20 })
            ForEach(this.items.slice().reverse(), (it: LegacyItem) => {
              Column() {
                Row() {
                  Text(`第 ${it.gen} 代`).fontSize(14).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
                  Blank()
                  Text(this.fmt(it.ended_at)).fontSize(11).fontColor('#5f6c96')
                }
                .width('100%')
                Text(it.summary)
                  .fontSize(12).lineHeight(18).fontColor('#9fb0d8')
                  .margin({ top: 8 })
                  .maxLines(5)
                  .textOverflow({ overflow: TextOverflow.Ellipsis })
                  .width('100%')
              }
              .width('100%').padding(14)
              .backgroundColor('#121826').borderRadius(14).margin({ top: 10 })
            }, (it: LegacyItem) => `${it.gen}`)
          }

          Text('每一代都会记得上一代最重要的事，但也会有自己的性格。')
            .fontSize(11).fontColor('#4a567c').margin({ top: 16, bottom: 30 }).width('100%')
        }
        .padding({ left: 16, right: 16 })
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
