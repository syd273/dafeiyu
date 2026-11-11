from PIL import Image, ImageDraw, ImageFilter
import struct, io, math
S = 256
img = Image.new("RGBA", (S, S), (5, 6, 12, 255))
d = ImageDraw.Draw(img)
# 星系光晕
for r, a in [(120, 26), (92, 40), (64, 60)]:
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    dl.ellipse((S//2 - r, S//2 - int(r*0.42), S//2 + r, S//2 + int(r*0.42)), fill=(255, 205, 140, a))
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, layer)
d = ImageDraw.Draw(img)
# 中心亮核
for rr in (30, 20, 12):
    d.ellipse((S//2 - rr, S//2 - rr//2 - 4, S//2 + rr, S//2 + rr//2 - 4), fill=(255, 244, 220, 160))
d.ellipse((S//2 - 12, S//2 - 8, S//2 + 12, S//2 + 4), fill=(255, 255, 250, 255))
# 星点
import random
random.seed(7)
for _ in range(160):
    x = random.randint(10, S-10); y = random.randint(10, S-10)
    dr = math.hypot(x-S//2, (y-S//2)/0.55)
    if dr > 118: continue
    a = max(40, int(255 - dr*1.7))
    d.ellipse((x, y, x+2, y+2), fill=(220, 232, 255, a))
img.save(r"D:\大肥鱼\记忆星图.ico", sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])
print("ico ok")