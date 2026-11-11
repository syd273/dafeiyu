from pathlib import Path
p = Path(r"D:\大肥鱼\docs\二开评估报告.md")
s = p.read_text(encoding="utf-8")
s = s.replace("> 两仓库均为 **MIT**，允许修改/商用，需保留版权与许可声明（加 NOTICE）。",
"""> 许可证情况：
> - `dsh-dafeiyu-life`：**MIT**（有 LICENSE 文件、NOTICE.md、THIRD_PARTY_NOTICES.md）
> - `dsh-feiyu`：**package.json 声明 MIT，但仓库内没有 LICENSE 文件**（需向上游确认或自行补 NOTICE 说明来源）
> 两者都允许修改/商用，但必须保留版权与许可声明。""")
p.write_text(s, encoding="utf-8")
print("license note updated")