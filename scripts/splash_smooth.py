from pathlib import Path
import json

# 1) 启动背景色统一为深色
for f in [r"D:\anshiyu_app\entry\src\main\resources\base\element\color.json",
          r"D:\anshiyu_app\entry\src\main\resources\dark\element\color.json"]:
    p = Path(f)
    d = json.loads(p.read_text(encoding="utf-8"))
    for c in d["color"]:
        if c["name"] == "start_window_background":
            c["value"] = "#0d1017"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("启动背景色 -> #0d1017")

# 2) EntryAbility：窗口背景色 + 键盘避让
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""        mainWindow.getUIContext().setKeyboardAvoidMode(KeyboardAvoidMode.RESIZE);""",
"""        // 窗口背景与页面同色，避免启动白屏/闪白
        try {
          mainWindow.setWindowBackgroundColor('#0d1017');
        } catch (e) { }
        mainWindow.getUIContext().setKeyboardAvoidMode(KeyboardAvoidMode.RESIZE);""")
p.write_text(s, encoding="utf-8")
print("EntryAbility 窗口背景已设置")

# 3) Index：页面淡入
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State bgImage: string = '';",
"""  @State bgImage: string = '';
  @State ready: boolean = false;""")
s = s.replace("""  aboutToAppear() {
    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
    });
  }""",
"""  aboutToAppear() {
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
  }""")
s = s.replace("""    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}""",
"""    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
    .opacity(this.ready ? 1 : 0)
  }
}""")
p.write_text(s, encoding="utf-8")
print("Index 淡入已加")