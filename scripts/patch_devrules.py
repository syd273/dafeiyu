from pathlib import Path

p = Path(r"D:\大肥鱼\docs\交互约定.md")
s = p.read_text(encoding="utf-8")
if "开发铁律" not in s:
    s += """

## 5. 开发铁律（2026-11-09 用户确认）

1. 本地完成度 ≈ 云端完成度时，交给本地 qwen2.5-coder:7b（含大型代码类任务），中途可向我反问
2. 开发不得影响电脑运行
3. 不得干扰 DSH 运行
4. 保护本地磁盘（只写 D:\\大肥鱼）
5. 绝对隔离校枢项目

详见 `docs/开发铁律.md`。
"""
    p.write_text(s, encoding="utf-8")
    print("interaction doc updated")

p = Path(r"D:\大肥鱼\docs\交接-安诗鱼App.md")
s = p.read_text(encoding="utf-8")
if "开发铁律" not in s:
    s += """

## 十一、开发铁律（用户明确要求）

见 `docs/开发铁律.md`：
- 能力接近时交本地 qwen2.5-coder:7b（校枢空闲时），大型代码类任务也可以，中途可反问
- 不影响电脑运行、不干扰 DSH、只写 D:\\大肥鱼、绝对隔离校枢
"""
    p.write_text(s, encoding="utf-8")
    print("handover updated")