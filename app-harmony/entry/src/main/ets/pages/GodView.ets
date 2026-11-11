// 上帝视角（横屏 WebView 展示 8899 上帝视角页面）
import { webview } from '@kit.ArkWeb';
import { window } from '@kit.ArkUI';
import router from '@ohos.router';
import { AppConfig } from '../common/Config';

@Entry
@Component
struct GodView {
  controller: webview.WebviewController = new webview.WebviewController();
  @State url: string = 'about:blank';
  @State ready: boolean = false;
  @State loaded: boolean = false;
  @State failed: boolean = false;
  private rotated: boolean = false;

  aboutToAppear() {
    this.enterFullscreen();
    this.maybeLandscape();
    this.loadUrl();
    setTimeout(() => { if (!this.loaded) { this.failed = true; } }, 6000);
  }

  aboutToDisappear() {
    if (this.rotated) { this.setOrientation(window.Orientation.PORTRAIT); }
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
      // 首页是沉浸式（layoutFullScreen=true），这里必须恢复成 true，
      // 否则状态栏会占真实高度 + 页面又留一次安全区 = 顶部多一条空白
      await win.setWindowLayoutFullScreen(true);
      await win.setWindowSystemBarEnable(['status', 'navigation']);
    } catch (e) { }
  }

  async loadUrl() {
    try {
      const ctx = getContext(this) as Context;
      const base = await AppConfig.getBase(ctx);
      this.url = base.replace(':8900', ':8899') + '/god.html';
      this.ready = true;
    } catch (e) {
      this.url = 'about:blank';
      this.ready = true;
    }
  }

  /** 仅在竖屏(窄屏)时才需要切横屏；折叠屏展开态本身够宽，直接用当前宽屏 */
  async maybeLandscape() {
    try {
      const win = await window.getLastWindow(getContext(this));
      const p = win.getWindowProperties().windowRect;
      if (p.height > p.width) {
        await win.setPreferredOrientation(window.Orientation.LANDSCAPE);
        this.rotated = true;
      }
    } catch (e) { }
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
          .onPageEnd(() => { if (!this.failed) { this.loaded = true; } })
          .onErrorReceive(() => { this.failed = true; })
          .backgroundColor('#0b0e16')
      } else {
        Column() {
          LoadingProgress().width(40).height(40).color('#5f6c96')
          Text('正在打开上帝视角…').fontSize(12).fontColor('#5f6c96').margin({ top: 10 })
        }
        .width('100%').height('100%').justifyContent(FlexAlign.Center)
        .backgroundColor('#0b0e16')
      }

      // 加载失败兜底：不让用户面对纯黑屏
      if (this.failed && !this.loaded) {
        Column() {
          Text('上帝视角没有连上').fontSize(16).fontColor('#cfe0ff').fontWeight(FontWeight.Medium)
          Text('请在设置里确认服务器地址，并确保电脑上的星图服务（8899 端口）已启动')
            .fontSize(12).fontColor('#5f6c96').textAlign(TextAlign.Center)
            .margin({ top: 10, left: 32, right: 32 })
          Button('返回聊天页').fontSize(13).height(34).margin({ top: 18 })
            .backgroundColor('#1a2138').fontColor('#cfe0ff')
            .onClick(() => { router.back(); })
        }
        .width('100%').height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#0b0e18')
      }

      Text('‹ 返回')
        .fontSize(14).fontColor('#cfe0ff')
        .padding({ left: 12, right: 12, top: 6, bottom: 6 })
        .backgroundColor('#11151fcc')
        .borderRadius(16)
        .position({ x: 16, y: 60 })
        .onClick(() => { router.back(); })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0b0e16')
  }
}
