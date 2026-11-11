from pathlib import Path
from PIL import Image

src_dir = Path(r"D:\大肥鱼\dist\screenshots")
out_dir = Path(r"D:\大肥鱼\dist\screenshots-listing")
out_dir.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
BG = (13, 16, 23)

def fit(path: Path, out: Path):
    im = Image.open(path).convert("RGB")
    # 等比缩放到画布内
    scale = min(W / im.width, H / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im2 = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(im2, ((W - nw) // 2, (H - nh) // 2))
    canvas.save(out, "PNG")
    print(out.name, "ok")

files = [
    ("01-chat.jpeg", "01-chat.png"),
    ("02-starmap.jpeg", "02-starmap.png"),
    ("03-godview.jpeg", "03-godview.png"),
    ("04-says.jpeg", "04-says.png"),
    ("05-settings.jpeg", "05-settings.png"),
]
for s, o in files:
    p = src_dir / s
    if p.exists():
        fit(p, out_dir / o)