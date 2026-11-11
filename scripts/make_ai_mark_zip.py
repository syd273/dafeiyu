from pathlib import Path
from PIL import Image

# 1) 说明文档（pdf 用 md 转不了，用图片+txt 打包）
doc = """AI 生成内容标识说明
应用名称：安诗鱼（com.anshiyu.app）

一、标识位置
在聊天界面中，每条 AI 角色回复的气泡下方均显示灰色小字「AI 生成」，用于明确告知用户该内容由人工智能生成。

二、标识样式
字体：9px，颜色：#4a567c（次要灰）
位置：回复气泡下方、左侧对齐
示例见附图（AI标识示例.png）

三、生成方式
对话内容由用户自行配置的第三方大语言模型（如 DeepSeek）生成，应用本身不训练模型、不提供模型服务。

四、内容安全
应用内置违法/隐私词库过滤，对违规内容进行拦截或替换。

五、用户告知
应用内提供《隐私政策》《用户协议》，均在设置页可查看；上架页面已关联协议链接。

日期：2026-11-11
"""
out = Path(r"D:\大肥鱼\dist\ai-mark")
out.mkdir(parents=True, exist_ok=True)
(out / "AI生成标识说明.txt").write_text(doc, encoding="utf-8")

# 2) 标识截图（从 demo_mode 裁剪聊天气泡区域）
src = Path(r"D:\大肥鱼\logs\demo_mode.jpeg")
if src.exists():
    im = Image.open(src).convert("RGB")
    # 裁剪中部（含 AI 生成标识）
    w, h = im.size
    crop = im.crop((0, int(h*0.18), w, int(h*0.40)))
    crop.save(out / "AI标识示例.png", "PNG")
    print("截图已裁剪", crop.size)

# 3) 打包 zip
import zipfile
z = out / "AI生成标识材料.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in out.iterdir():
        if f.suffix in (".txt", ".png"):
            zf.write(f, f.name)
print("打包:", z, z.stat().st_size, "bytes")