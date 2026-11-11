import json
from pathlib import Path

# 1) module.json5 加长时任务权限
p = Path(r"D:\anshiyu_app\entry\src\main\module.json5")
s = p.read_text(encoding="utf-8")
if "KEEP_BACKGROUND_RUNNING" not in s:
    s = s.replace('"name": "ohos.permission.INTERNET"',
'''"name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.KEEP_BACKGROUND_RUNNING"''')
    p.write_text(s, encoding="utf-8")
    print("KEEP_BACKGROUND_RUNNING 权限已加")

# 2) EntryAbility 前后台长时任务
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { window, KeyboardAvoidMode } from '@kit.ArkUI';",
"""import { window, KeyboardAvoidMode } from '@kit.ArkUI';
import { backgroundTaskManager } from '@kit.BackgroundTasksKit';
import { wantAgent, WantAgent } from '@kit.AbilityKit';""")

s = s.replace("""  onForeground(): void {
    // Ability has brought to foreground
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onForeground');
  }

  onBackground(): void {
    // Ability has back to background
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onBackground');
  }""",
"""  onForeground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onForeground');
    try {
      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e) => { });
    } catch (e) { }
  }

  onBackground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onBackground');
    // 后台保持连接，收到她的消息时发通知
    try {
      const info: wantAgent.WantAgentInfo = {
        wants: [
          {
            bundleName: 'com.anshiyu.app',
            abilityName: 'EntryAbility',
          } as wantAgent.WantAgentInfo,
        ],
        actionType: wantAgent.OperationType.START_ABILITY,
        requestCode: 0,
        wantAgentFlags: [wantAgent.WantAgentFlags.UPDATE_PRESENT_FLAG],
      };
      wantAgent.getWantAgent(info).then((agent: WantAgent) => {
        backgroundTaskManager.startBackgroundRunning(
          this.context,
          backgroundTaskManager.BackgroundMode.DATA_TRANSFER,
          agent
        ).catch((e) => { });
      }).catch((e) => { });
    } catch (e) { }
  }""")
p.write_text(s, encoding="utf-8")
print("EntryAbility 长时任务已加")