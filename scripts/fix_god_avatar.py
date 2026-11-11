from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\god.html")
s = p.read_text(encoding="utf-8")
s = s.replace("url('https://i0.hdslb.com/bfs/archive/c6baa32df983b82a29acc3c2a8736c65f598984d.jpg')", "url('avatar.png')")
p.write_text(s, encoding="utf-8")
print("头像已换本地")