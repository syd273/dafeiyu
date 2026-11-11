from PIL import Image, ImageDraw, ImageFilter
import math, random
S = 512
img = Image.new("RGBA", (S, S), (0, 0, 0, 255))
# 深蓝渐变背景
for y in range(S):
    r = int(10 + 18 * y / S)
    g = int(16 + 24 * y / S)
    b = int(34 + 40 * y / S)
    ImageDraw.Draw(img).line([(0, y), (S, y)], fill=(r, g, b, 255))
# 星点
random.seed(7)
d = ImageDraw.Draw(img)
for _ in range(260):
    x, y = random.randint(0, S-1), random.randint(0, S-1)
    a = random.randint(90, 255)
    s = random.choice([1, 1, 1, 2])
    d.ellipse((x, y, x + s, y + s), fill=(210, 225, 255, a))
# 中心光晕
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for rad, alpha in ((150, 40), (110, 60), (75, 90)):
    gd.ellipse((S//2-rad, S//2-rad, S//2+rad, S//2+rad), fill=(140, 170, 255, alpha))
glow = glow.filter(ImageFilter.GaussianBlur(18))
img = Image.alpha_composite(img, glow)
d = ImageDraw.Draw(img)
# 一条小鱼（简单剪影）
cx, cy = S // 2, S // 2 + 20
body = [(cx - 120, cy), (cx - 40, cy - 55), (cx + 90, cy - 42), (cx + 130, cy),
        (cx + 90, cy + 42), (cx - 40, cy + 55)]
d.polygon(body, fill=(235, 242, 255, 235))
tail = [(cx - 120, cy), (cx - 190, cy - 55), (cx - 165, cy), (cx - 190, cy + 55)]
d.polygon(tail, fill=(200, 215, 245, 220))
# 眼睛
d.ellipse((cx + 10, cy - 16, cx + 30, cy + 4), fill=(30, 42, 80, 255))
# 圆角裁剪
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse((0, 0, S, S), fill=255)
out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
out.paste(img, (0, 0), mask)
out.save(r"D:\大肥鱼\app-assets\anshiyu_avatar.png")
print("avatar saved")