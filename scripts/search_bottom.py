from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
s = s.replace("""<div id="memSearch">""",
"""<div id="memSearch" style="position:fixed;left:50%;transform:translateX(-50%);bottom:44px;z-index:18;width:340px;
  background:rgba(8,10,20,.88);border:1px solid rgba(120,150,220,.3);border-radius:12px;
  padding:8px 10px;backdrop-filter:blur(8px)">""")
p.write_text(s, encoding="utf-8")
print("搜索面板改为底部居中")