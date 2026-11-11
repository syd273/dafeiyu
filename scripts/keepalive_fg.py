from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")

# 改为：前台启动长时任务，后台保持，销毁时停止
s = s.replace("""  onForeground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onForeground');
    try {
      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e: Error) => { });
    } catch (e) { }
  }

  onBackground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onBackground');
    // 后台保持连接，收到她的消息时发通知
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
  }""",
"""  onForeground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onForeground');
    this.startKeepAlive();
  }

  onBackground(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onBackground');
    this.startKeepAlive();
  }

  onDestroy(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy');
    try {
      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e: Error) => { });
    } catch (e) { }
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
  }""")
p.write_text(s, encoding="utf-8")
print("keepalive updated")