import { AbilityConstant, ConfigurationConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window, KeyboardAvoidMode } from '@kit.ArkUI';
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { wantAgent, WantAgent } from '@kit.AbilityKit';

const DOMAIN = 0x0000;

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onCreate');
  }

  onDestroy(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy');
    try {
      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e: Error) => { });
    } catch (e) { }
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    // Main window is created, set main page for this ability
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onWindowStageCreate');

    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(DOMAIN, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err));
        return;
      }
      hilog.info(DOMAIN, 'testTag', 'Succeeded in loading the content.');
    });

    // 键盘避让：压缩布局（页面变矮，输入框跟着键盘，消息区仍可见）
    try {
      windowStage.getMainWindow((err, mainWindow) => {
        if (err.code) {
          return;
        }
        // 窗口背景与页面同色，避免启动白屏/闪白
        try {
          mainWindow.setWindowBackgroundColor('#0d1017');
        } catch (e) { }
        // 状态栏：沉浸式 + 深色背景浅色图标；读取安全区高度给页面留白
        try {
          mainWindow.setWindowLayoutFullScreen(true);
          mainWindow.setWindowSystemBarProperties({
            statusBarColor: '#0d1017',
            statusBarContentColor: '#ffffff',
            navigationBarColor: '#0d1017',
            navigationBarContentColor: '#ffffff',
          });
        } catch (e) { }
        try {
          const avoid = mainWindow.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
          const top = px2vp(avoid.topRect.height);
          AppStorage.setOrCreate('statusBarHeight', top);
        } catch (e) { }
        // 底部避让 = 三键导航栏(TYPE_SYSTEM.bottomRect) + 手势横条(TYPE_NAVIGATION_INDICATOR)
        // 两者互斥，同一时刻只有一个有值，必须相加才是真实占用高度
        const bottomAvoidVp = (w: window.Window): number => {
          const sys = w.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
          const ind = w.getWindowAvoidArea(window.AvoidAreaType.TYPE_NAVIGATION_INDICATOR);
          return px2vp(sys.bottomRect.height) + px2vp(ind.bottomRect.height);
        };
        try {
          const navH = bottomAvoidVp(mainWindow);
          AppStorage.setOrCreate('navBarHeight', navH > 0 ? navH : 28);
          hilog.info(DOMAIN, 'testTag', 'navBarHeight(init)=%{public}s', String(navH > 0 ? navH : 28) + 'vp');
        } catch (e) {
          AppStorage.setOrCreate('navBarHeight', 28);
        }
        // 折叠/展开、横竖屏旋转、手势条与三键切换都会改变避让区，
        // 必须实时同步，否则 Mate X7 这类折叠机切换形态后输入栏又被压住
        try {
          mainWindow.on('avoidAreaChange', (data: window.AvoidAreaOptions) => {
            try {
              const h = bottomAvoidVp(mainWindow);
              AppStorage.setOrCreate('navBarHeight', h > 0 ? h : 28);
            } catch (e) { }
          });
        } catch (e) { }
        try {
          mainWindow.on('windowSizeChange', () => {
            try {
              const h = bottomAvoidVp(mainWindow);
              AppStorage.setOrCreate('navBarHeight', h > 0 ? h : 28);
            } catch (e) { }
          });
        } catch (e) { }
        mainWindow.getUIContext().setKeyboardAvoidMode(KeyboardAvoidMode.RESIZE);
        // 主页锁竖屏：聊天/设置等页面不做横屏布局；
        // 星图、上帝视角会在各自页面里临时改成横屏，退出时再恢复竖屏
        try { mainWindow.setPreferredOrientation(window.Orientation.PORTRAIT); } catch (e) { }
      });
    } catch (err) {
      hilog.error(DOMAIN, 'testTag', 'Failed to set keyboard avoid mode. Cause: %{public}s', JSON.stringify(err));
    }

    try {
      this.context.getApplicationContext().setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET);
    } catch (err) {
      hilog.error(DOMAIN, 'testTag', 'Failed to set colorMode. Cause: %{public}s', JSON.stringify(err));
    }
  }

  onWindowStageDestroy(): void {
    // Main window is destroyed, release UI related resources
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onWindowStageDestroy');
  }

  onForeground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onForeground');
    this.startKeepAlive();
  }

  onBackground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onBackground');
    this.startKeepAlive();
  }

  /** 长时任务：保持后台连接，收到她的消息时发通知 */
  startKeepAlive(): void {
    try {
      const want: Want = {
        bundleName: 'com.anshiyu.app',
        abilityName: 'EntryAbility',
      };
      const info: wantAgent.WantAgentInfo = {
        wants: [want],
        actionType: wantAgent.OperationType.START_ABILITY,
        requestCode: 0,
        wantAgentFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG],
      };
      wantAgent.getWantAgent(info).then((agent: WantAgent) => {
        backgroundTaskManager.startBackgroundRunning(
          this.context,
          backgroundTaskManager.BackgroundMode.DATA_TRANSFER,
          agent
        ).catch((e: Error) => { });
      }).catch((e: Error) => { });
    } catch (e) { }
  }
}