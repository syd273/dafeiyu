from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Legacy.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("const req = http.createAsyncHttp();", "const req = http.createHttp();")
s = s.replace("""      if (d.ok) {
        this.tip = `第 ${d.gen} 代已结束，第 ${(d.gen as number) + 1} 代开始了`;
      } else {""",
"""      if (d.ok) {
        const gen = (d.gen ?? 0) as number;
        this.tip = `第 ${gen} 代已结束，第 ${gen + 1} 代开始了`;
      } else {""")
p.write_text(s, encoding="utf-8")
print("已修复")