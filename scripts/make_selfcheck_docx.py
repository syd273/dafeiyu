from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

out = Path(r"D:\大肥鱼\dist\自测说明-安诗鱼.docx")
doc = Document()

title = doc.add_heading("安诗鱼 · 审核自测说明", level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_heading("一、应用定位", level=1)
doc.add_paragraph(
    "本应用是个人 AI 陪伴客户端工具，不内置任何大模型 API Key，不向用户提供 AI 服务。"
    "用户需自行配置自己的服务端与大模型 API（如 DeepSeek）。全部数据（聊天、记忆、备份）"
    "仅保存在用户自己的设备上。"
)

doc.add_heading("二、审核体验方式（无需任何配置）", level=1)
doc.add_paragraph(
    "应用启动后若未连接服务端，会自动进入「演示模式」：展示示例对话与完整界面，"
    "顶部显示『离线』并可点击『重连』。审核人员无需配置服务器即可体验聊天界面、"
    "记忆星图、说说、设置等功能。"
)

doc.add_heading("三、如需连接真实服务（可选）", level=1)
doc.add_paragraph("1. 在设置 → 本地服务器 填写服务端地址；")
doc.add_paragraph("2. 设置 → DeepSeek API Key 填入自己的 Key；")
doc.add_paragraph("3. 点击「测试连接」「测试 Key」验证；")
doc.add_paragraph("4. 详见应用内「配置教程」。")

doc.add_heading("四、内容安全", level=1)
doc.add_paragraph("· 内置违法/隐私词库过滤（赌博、毒品、隐私查询等）；")
doc.add_paragraph("· AI 生成内容在气泡下方标注「AI 生成」；")
doc.add_paragraph("· 用户协议明确禁止违法用途；")
doc.add_paragraph("· 提供隐私政策与用户协议链接。")

doc.add_heading("五、截图", level=1)
for name in ["演示模式.png", "聊天示例.png", "AI标识示例.png"]:
    p = Path(r"D:\大肥鱼\dist\ai-mark") / name
    if p.exists():
        doc.add_picture(str(p), width=Inches(5))

doc.add_paragraph("")
doc.add_paragraph("日期：2026-11-11")

doc.save(out)
print("已生成:", out, out.stat().st_size, "bytes")