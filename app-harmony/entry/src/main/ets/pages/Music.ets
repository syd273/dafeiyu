// 一起听歌：她从 B站 音乐区选歌，陪你听
import http from '@ohos.net.http';
import router from '@ohos.router';
import { AppConfig } from '../common/Config';
import { common } from '@kit.AbilityKit';

const TOKEN = 'anshiyu-app-2026';

interface Song {
  title: string;
  owner: string;
  bvid: string;
  url: string;
  pic: string;
}

@Entry
@Component
struct Music {
  @State song: Song | null = null;
  @State text: string = '';
  @State loading: boolean = false;
  @State baseUrl: string = '';
  @State shareText: string = '';

  aboutToAppear() {
    this.init();
  }

  async init() {
    const ctx = getContext(this) as Context;
    this.baseUrl = await AppConfig.getBase(ctx);
    await this.next();
  }

  async next() {
    this.loading = true;
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/music/recommend?token=${TOKEN}`, {
        method: http.RequestMethod.GET, connectTimeout: 10000, readTimeout: 60000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        if (d.ok) {
          this.song = d.song as Song;
          this.text = (d.text ?? '') as string;
        } else {
          this.text = '暂时没找到歌，稍后再试';
        }
      }
    } catch (e) {
      this.text = '连接失败，检查服务器';
    }
    this.loading = false;
  }

  async talk() {
    if (!this.song) return;
    this.loading = true;
    try {
      const req = http.createHttp();
      const url = `${this.baseUrl}/api/music/talk?token=${TOKEN}&title=${encodeURIComponent(this.song.title)}&owner=${encodeURIComponent(this.song.owner)}`;
      const res = await req.request(url, {
        method: http.RequestMethod.GET, connectTimeout: 10000, readTimeout: 60000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        if (d.ok) this.text = (d.text ?? '') as string;
      }
    } catch (e) { }
    this.loading = false;
  }

  async share() {
    const t = this.shareText.trim();
    if (!t) return;
    this.loading = true;
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl}/api/music/share?token=${TOKEN}`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ text: t }),
        connectTimeout: 10000, readTimeout: 60000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        this.song = d.song as Song;
        this.text = (d.text ?? '') as string;
        this.shareText = '';
      } else {
        this.text = (d.error ?? '分享失败') as string;
      }
    } catch (e) {
      this.text = '分享失败，检查网络或链接';
    }
    this.loading = false;
  }

  async openSong() {
    if (!this.song) return;
    const ctx = getContext(this) as common.UIAbilityContext;
    const uri = `bilibili://video/${this.song.bvid}`;
    try {
      await ctx.startAbility({
        action: 'ohos.want.action.viewData',
        uri: uri,
        entities: ['entity.system.browsable'],
      });
    } catch (e) {
      try {
        await ctx.startAbility({
          action: 'ohos.want.action.viewData',
          uri: this.song.url,
          entities: ['entity.system.browsable'],
        });
      } catch (e2) { }
    }
  }

  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('一起听歌').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text('🎧').fontSize(18)
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      Scroll() {
        Column() {
          // 分享一首歌给她
          Row() {
            TextInput({ text: this.shareText, placeholder: '粘贴 B站 视频链接，分享给她' })
              .layoutWeight(1)
              .fontSize(13).fontColor('#e8eeff').placeholderColor('#5f6c96')
              .backgroundColor('#161b29').borderRadius(12)
              .onChange((v: string) => { this.shareText = v; })
            Button('分享')
              .height(36).width(56).margin({ left: 8 })
              .backgroundColor('#3b6ef5').fontSize(13).fontColor('#ffffff')
              .borderRadius(18)
              .enabled(!this.loading && this.shareText.trim().length > 0)
              .onClick(() => { this.share(); })
          }
          .width('100%')
          .margin({ top: 12 })

          if (this.song) {
            // 封面
            if (this.song.pic) {
              Image(this.song.pic)
                .width('100%')
                .aspectRatio(1)
                .objectFit(ImageFit.Cover)
                .borderRadius(16)
                .margin({ top: 16 })
            }
            // 歌名/UP
            Text(this.song.title)
              .fontSize(17).fontWeight(FontWeight.Medium).fontColor('#eef2ff')
              .margin({ top: 14 })
              .width('100%')
            Text(this.song.owner)
              .fontSize(12).fontColor('#6f7fae').margin({ top: 6 }).width('100%')

            // 她的话
            Text(this.text)
              .fontSize(15).lineHeight(22).fontColor('#cfe0ff')
              .padding(14)
              .backgroundColor('#161d2e')
              .borderRadius(14)
              .margin({ top: 16 })
              .width('100%')
          } else {
            Column() {
              LoadingProgress().width(36).height(36).color('#5f6c96')
              Text(this.loading ? '她正在挑歌…' : this.text)
                .fontSize(13).fontColor('#5f6c96').margin({ top: 10 })
            }
            .width('100%').height(300).justifyContent(FlexAlign.Center)
          }

          // 按钮
          Row() {
            Button('换一首')
              .height(40).layoutWeight(1)
              .backgroundColor('#232d47').fontSize(14).fontColor('#cfe0ff')
              .borderRadius(20)
              .enabled(!this.loading)
              .onClick(() => { this.next(); })
            Button('让她说说')
              .height(40).layoutWeight(1).margin({ left: 10 })
              .backgroundColor('#232d47').fontSize(14).fontColor('#cfe0ff')
              .borderRadius(20)
              .enabled(!this.loading && this.song !== null)
              .onClick(() => { this.talk(); })
          }
          .width('100%')
          .margin({ top: 16 })

          Button('打开这首歌（B站）')
            .height(44).width('100%').margin({ top: 10 })
            .backgroundColor('#3b6ef5').fontSize(15).fontColor('#ffffff')
            .borderRadius(22)
            .enabled(this.song !== null)
            .onClick(() => { this.openSong(); })

          Text('一起听歌 · 她挑歌你听，听完可以让她说说感受')
            .fontSize(11).fontColor('#4a567c').margin({ top: 18, bottom: 20 })
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
