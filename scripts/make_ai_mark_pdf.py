from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import zipfile

out = Path(r"D:\大肥鱼\dist\ai-mark")
out.mkdir(parents=True, exist_ok=True)

text = """AI 生成内容标识说明

应用名称：安诗鱼（com.anshiyu.app）

一、标识位置
聊天界面中，每条 AI 角色回复的气泡下方均显示灰色小字「AI 生成」，明确告知用户该内容由人工智能生成。

二、标识样式
字体 9px，颜色 #4a567c（次要灰），位于回复气泡下方左侧对齐。示例见附图。

三、生成方式
对话内容由用户自行配置的第三方大语言模型（如 DeepSeek）生成；应用本身不训练模型、不提供模型服务。

四、内容安全
应用内置违法/隐私词库过滤，对违规内容拦截或替换。

五、用户告知
应用内提供《隐私政策》《用户协议》，设置页可查看。

日期：2026-11-11
"""

font_path = r"C:\Windows\Fonts\msyh.ttc"
font = ImageFont.truetype(font_path, 28)
title_font = ImageFont.truetype(font_path, 36)

W, H = 1240, 1754  # A4 比例
img = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(img)
y = 90
d.text((80, y), "AI 生成内容标识说明", font=title_font, fill=(0, 0, 0))
y += 70
for line in text.split("\n")[1:]:
    if not line.strip():
        y += 24
        continue
    d.text((80, y), line, font=font, fill=(30, 30, 30))
    y += 44
img.save(out / "AI生成标识说明.jpg", "JPEG", quality=92)

# 示例截图转 JPG
src = out / "AI标识示例.png"
if src.exists():
    Image.open(src).convert("RGB").save(out / "AI标识示例.jpg", "JPEG", quality=90)

z = out / "AI生成标识材料.zip"
if z.exists():
    z.unlink()
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(out / "AI生成标识说明.jpg", "AI生成标识说明.jpg")
    if (out / "AI标识示例.jpg").exists():
        zf.write(out / "AI标识示例.jpg", "AI标识示例.jpg")
print("已生成 zip:", z.stat().st_size, "bytes")