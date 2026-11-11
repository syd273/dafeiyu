from pathlib import Path

p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# 记录启动时间
s = s.replace("  private lastAssistant: string = '';",
"""  private splashStart: number = 0;
  private lastAssistant: string = '';""")

s = s.replace("""  aboutToAppear() {
    this.startSplash();""",
"""  aboutToAppear() {
    this.splashStart = Date.now();
    this.startSplash();""")

# finishSplash：至少展示 800ms
s = s.replace("""  finishSplash() {
    if (!this.showSplash) return;
    this.getUIContext().animateTo({ duration: 260, curve: Curve.EaseInOut }, () => {
      this.splashOpacity = 0;
    });
    setTimeout(() => { this.showSplash = false; }, 280);
  }""",
"""  finishSplash() {
    if (!this.showSplash) return;
    const elapsed = Date.now() - this.splashStart;
    const wait = Math.max(0, 800 - elapsed);
    setTimeout(() => {
      this.getUIContext().animateTo({ duration: 300, curve: Curve.EaseInOut }, () => {
        this.splashOpacity = 0;
      });
      setTimeout(() => { this.showSplash = false; }, 320);
    }, wait);
  }""")
p.write_text(s, encoding="utf-8")
print("splash min duration fixed")