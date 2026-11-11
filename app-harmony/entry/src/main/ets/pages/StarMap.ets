// 记忆星图（横屏 WebView 展示 8899 星图服务）
import { webview } from '@kit.ArkWeb';
import { window } from '@kit.ArkUI';
import router from '@ohos.router';
import { AppConfig } from '../common/Config';

@Entry
@Component
struct StarMap {
  controller: webview.WebviewController = new webview.WebviewController();
  @State url: string = 'about:blank';
  @State ready: boolean = false;

  aboutToAppear() {
    this.enterFullscreen();
    this.setOrientation(window.Orientation.LANDSCAPE);
    this.loadUrl();
  }

  aboutToDisappear() {
    this.setOrientation(window.Orientation.PORTRAIT);
    this.exitFullscreen();
  }

  async enterFullscreen() {
    try {
      const win = await window.getLastWindow(getContext(this));
      await win.setWindowLayoutFullScreen(true);
      await win.setWindowSystemBarEnable([]);
    } catch (e) { }
  }

  async exitFullscreen() {
    try {
      const win = await window.getLastWindow(getContext(this));
      await win.setWindowLayoutFullScreen(false);
      await win.setWindowSystemBarEnable(['status', 'navigation']);
    } catch (e) { }
  }

  async loadUrl() {
    try {
      const ctx = getContext(this) as Context;
      const base = await AppConfig.getBase(ctx);
      this.url = base.replace(':8900', ':8899');
      this.ready = true;
    } catch (e) {
      this.url = 'about:blank';
      this.ready = true;
    }
  }

  async setOrientation(orientation: window.Orientation) {
    try {
      const win = await window.getLastWindow(getContext(this));
      await win.setPreferredOrientation(orientation);
    } catch (e) { }
  }

  build() {
    Stack() {
      if (this.ready) {
        Web({ src: this.url, controller: this.controller })
          .width('100%')
          .height('100%')
          .darkMode(WebDarkMode.On)
          .backgroundColor('#0b0e18')
      } else {
        Column() {
          LoadingProgress().width(40).height(40).color('#5f6c96')
          Text('正在打开星图…').fontSize(12).fontColor('#5f6c96').margin({ top: 10 })
        }
        .width('100%').height('100%').justifyContent(FlexAlign.Center)
        .backgroundColor('#0b0e18')
      }

      // 返回按钮
      Text('‹ 返回')
        .fontSize(14).fontColor('#cfe0ff')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#11151fcc')
        .borderRadius(16)
        .position({ x: 16, y: 16 })
        .onClick(() => { router.back(); })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0b0e18')
  }
}
