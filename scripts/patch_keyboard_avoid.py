from pathlib import Path

# 1) EntryAbility：键盘避让模式改为 RESIZE（压缩布局，输入框跟随键盘）
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { window } from '@kit.ArkUI';",
              "import { window, KeyboardAvoidMode } from '@kit.ArkUI';")
s = s.replace("""      hilog.info(DOMAIN, 'testTag', 'Succeeded in loading the content.');
    });""",
"""      hilog.info(DOMAIN, 'testTag', 'Succeeded in loading the content.');
    });

    // 键盘避让：压缩布局（页面变矮，输入框跟着键盘，消息区仍可见）
    try {
      windowStage.getMainWindow((err, mainWindow) => {
        if (err.code) {
          return;
        }
        mainWindow.getUIContext().setKeyboardAvoidMode(KeyboardAvoidMode.RESIZE);
      });
    } catch (err) {
      hilog.error(DOMAIN, 'testTag', 'Failed to set keyboard avoid mode. Cause: %{public}s', JSON.stringify(err));
    }""")
p.write_text(s, encoding="utf-8")
print("EntryAbility patched")

# 2) Index：发送后延迟滚动到底（等键盘动画完成），并让列表可滚动到最新
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""    setTimeout(() => {
      try { this.scroller.scrollEdge(Edge.Bottom); } catch (e) { }
    }, 60);""",
"""    // 键盘弹出/收起有动画，稍晚再滚到底部
    setTimeout(() => {
      try { this.scroller.scrollEdge(Edge.Bottom); } catch (e) { }
    }, 120);
    setTimeout(() => {
      try { this.scroller.scrollEdge(Edge.Bottom); } catch (e) { }
    }, 350);""")
p.write_text(s, encoding="utf-8")
print("Index scroll patched")