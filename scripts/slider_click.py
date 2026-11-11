from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("if (mode === SliderChangeMode.End) { this.savePersona(); }",
              "if (mode === SliderChangeMode.End || mode === SliderChangeMode.Click) { this.savePersona(); }")
p.write_text(s, encoding="utf-8")
print("滑块保存条件已改")