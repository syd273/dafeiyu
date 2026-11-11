from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# 1) 状态：换成启动动画状态
s = s.replace("""  @State bgImage: string = '';
  @State ready: boolean = false;""",
"""  @State bgImage: string = '';
  @State showSplash: boolean = true;
  @State splashOpacity: number = 1;
  @State logoOpacity: number = 0;
  @State logoScale: number = 0.86;
  @State titleOpacity: number = 0;
  @State titleOffset: number = 14;""")

# 2) aboutToAppear：启动动画 + 就绪收尾
s = s.replace("""  aboutToAppear() {
    // 页面淡入，避免启动时生硬切换
    setTimeout(() => {
      this.getUIContext().animateTo({ duration: 220, curve: Curve.EaseOut }, () => {
        this.ready = true;
      });
    }, 40);
    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
    });
  }""",
"""  aboutToAppear() {
    this.startSplash();
    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
      this.finishSplash();
    }).catch(() => {
      this.finishSplash();
    });
    // 兜底：最多 1.2 秒结束启动动画
    setTimeout(() => { this.finishSplash(); }, 1200);
  }

  startSplash() {
    // Logo 淡入 + 缩放
    this.getUIContext().animateTo({ duration: 600, curve: Curve.EaseOut, delay: 80 }, () => {
      this.logoOpacity = 1;
      this.logoScale = 1;
    });
    // 名称与签名淡入 + 上移
    this.getUIContext().animateTo({ duration: 420, curve: Curve.EaseOut, delay: 300 }, () => {
      this.titleOpacity = 1;
      this.titleOffset = 0;
    });
  }

  finishSplash() {
    if (!this.showSplash) return;
    this.getUIContext().animateTo({ duration: 260, curve: Curve.EaseInOut }, () => {
      this.splashOpacity = 0;
    });
    setTimeout(() => { this.showSplash = false; }, 280);
  }""")

# 3) build 外层改为 Stack：主界面 + 启动层
s = s.replace("""  build() {
    Column() {
      // ===== 顶部导航栏 =====""",
"""  build() {
    Stack() {
      this.mainView()

      if (this.showSplash) {
        Column() {
          Image($r('app.media.startIcon'))
            .width(132).height(132)
            .opacity(this.logoOpacity)
            .scale({ x: this.logoScale, y: this.logoScale })
          Text('安诗鱼')
            .fontSize(24).fontWeight(FontWeight.Medium).fontColor('#eef2ff')
            .opacity(this.titleOpacity)
            .offset({ y: this.titleOffset })
            .margin({ top: 20 })
          Text('她有自己的生活，也会想你')
            .fontSize(13).fontColor('#66739d')
            .opacity(this.titleOpacity)
            .offset({ y: this.titleOffset })
            .margin({ top: 10 })
        }
        .width('100%').height('100%')
        .justifyContent(FlexAlign.Center)
        .backgroundColor('#0d1017')
        .opacity(this.splashOpacity)
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }

  @Builder
  mainView() {
    Column() {
      // ===== 顶部导航栏 =====""")

# 4) 主界面根 Column 去掉 opacity(ready)
s = s.replace("""    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
    .opacity(this.ready ? 1 : 0)
  }
}""",
"""    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}""")

p.write_text(s, encoding="utf-8")
print("splash animation added")