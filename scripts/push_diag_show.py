from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State nightlyReflect: boolean = true;",
              "  @State nightlyReflect: boolean = true;\n  @State diagMsg: string = '';")
s = s.replace("""              .onClick(() => {
                PushHelper.diagnose(this.baseUrl2).then((msg: string) => {
                  this.tip = msg;
                });
              })""",
"""              .onClick(() => {
                this.diagMsg = '检测中…';
                PushHelper.diagnose(this.baseUrl2).then((msg: string) => {
                  this.diagMsg = msg;
                }).catch((e: Error) => {
                  this.diagMsg = '检测异常: ' + e.message;
                });
              })
            if (this.diagMsg) {
              Text(this.diagMsg)
                .fontSize(11).fontColor('#ffd48a')
                .width('100%').margin({ top: 6 })
                .maxLines(3)
            }""")
p.write_text(s, encoding="utf-8")
print("诊断结果显示已加")