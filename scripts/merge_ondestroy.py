from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")
# 删除新增的重复 onDestroy 块
dup = """  onDestroy(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy');
    try {
      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e: Error) => { });
    } catch (e) { }
  }

"""
s = s.replace(dup, "")
# 原有 onDestroy 加停止逻辑
s = s.replace("""  onDestroy(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy');
  }""",
"""  onDestroy(): void {
    hilog.info(DOMAIN, 'testTag', '%{public}s', 'Ability onDestroy');
    try {
      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e: Error) => { });
    } catch (e) { }
  }""")
p.write_text(s, encoding="utf-8")
print("onDestroy merged")