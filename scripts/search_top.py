from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
s = s.replace("bottom:44px;z-index:18;width:340px;",
              "top:10px;z-index:18;width:340px;")
p.write_text(s, encoding="utf-8")
print("搜索面板移到顶部")