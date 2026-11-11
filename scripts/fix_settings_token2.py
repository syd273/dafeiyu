from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
if "let TOKEN" not in s:
    s = s.replace("const THEMES: string[] = [",
"""let TOKEN = 'anshiyu-app-2026';

const THEMES: string[] = [""")
    p.write_text(s, encoding="utf-8")
    print("TOKEN 已插入")
else:
    print("已存在")