from pathlib import Path
from PIL import Image
src = Path(r"D:\anshiyu_app\entry\src\main\resources\base\media\foreground.png")
out_dir = Path(r"D:\大肥鱼\dist")
out_dir.mkdir(parents=True, exist_ok=True)
fg = Image.open(src).convert("RGBA")
size = 1024
bg = Image.new("RGBA", (size, size), (13, 16, 23, 255))
fg = fg.resize((size, size), Image.LANCZOS)
bg.alpha_composite(fg)
bg.convert("RGB").save(out_dir / "app-icon-1024.png", "PNG")
print("已生成", out_dir / "app-icon-1024.png", bg.size)