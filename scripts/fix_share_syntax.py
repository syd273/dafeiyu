from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("this.tip = '保存失败');", "this.tip = '保存失败';")
p.write_text(s, encoding="utf-8")
print("语法修复")