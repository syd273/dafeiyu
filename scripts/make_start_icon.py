from PIL import Image, ImageDraw, ImageFilter
from collections import deque

SRC = r"C:\Users\SYD\.dsh\attachments\v1\objects\6c\6c1add3748bb8138c97491ab0d3e9033c0e07619cf62fc513752c29701004a82"
OUT = r"D:\大肥鱼\app-assets\startIcon.png"

img = Image.open(SRC).convert("RGBA")
w, h = img.size
px = img.load()
visited = [[False] * h for _ in range(w)]
q = deque()
for x in range(w):
    q.append((x, 0)); q.append((x, h - 1))
for y in range(h):
    q.append((0, y)); q.append((w - 1, y))
def near_white(c):
    return c[0] > 235 and c[1] > 235 and c[2] > 235
while q:
    x, y = q.popleft()
    if x < 0 or y < 0 or x >= w or y >= h or visited[x][y]:
        continue
    visited[x][y] = True
    c = px[x, y]
    if not near_white(c):
        continue
    px[x, y] = (255, 255, 255, 0)
    q.extend([(x+1,y),(x-1,y),(x,y+1),(x,y-1)])

bbox = img.getbbox()
content = img.crop(bbox)
cw, ch = content.size
S = 512
D = 460  # 圆形直径
scale = min(D / cw, D / ch) * 0.95
neww, newh = int(cw * scale), int(ch * scale)
content = content.resize((neww, newh), Image.LANCZOS)

# 圆形浅蓝底
canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse(((S-D)//2, (S-D)//2, (S+D)//2, (S+D)//2), fill=255)
circle = Image.new("RGBA", (S, S), (0, 0, 0, 0))
cd = ImageDraw.Draw(circle)
cx, cy = S // 2, S // 2
for i in range(D, 0, -2):
    t = i / D
    r = int(214 + 20 * (1 - t))
    g = int(228 + 14 * (1 - t))
    b = int(250 + 4 * (1 - t))
    cd.ellipse((cx - i//2, cy - i//2, cx + i//2, cy + i//2), fill=(r, g, b, 255))
canvas.paste(circle, (0, 0), mask)

# 角色叠在圆上（略大一点，超出圆形一点也可以，做裁剪）
logo = Image.new("RGBA", (S, S), (0, 0, 0, 0))
logo.paste(content, ((S - neww) // 2, (S - newh) // 2), content)
logo.save(OUT)
print("startIcon saved", OUT)