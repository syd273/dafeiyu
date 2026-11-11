from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace(".onClick(() => { this.loadConfig().then(() => this.loadStatus()); })",
              ".onClick(() => { this.loadConfig().then(() => { this.loadStatus(); }); })")
# 顺便把 aboutToAppear 的 then 也改成块体，避免同类问题
s = s.replace("""    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
    });""",
"""    this.loadConfig().then(() => {
      this.loadStatus();
      this.connectWs();
    }).catch(() => { });""")
p.write_text(s, encoding="utf-8")
print("patched")