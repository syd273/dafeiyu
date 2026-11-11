from pathlib import Path

# 1) index.html：去掉内联定位，交给 CSS
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
s = s.replace("""<div id="memSearch" style="position:fixed;left:24px;top:24px;z-index:18;width:230px;
  background:rgba(8,10,20,.85);border:1px solid rgba(120,150,220,.3);border-radius:12px;
  padding:8px 10px;backdrop-filter:blur(8px)">""",
"""<div id="memSearch">""")
p.write_text(s, encoding="utf-8")
print("index.html 搜索面板内联样式已移除")

# 2) style.css：基础样式 + 横屏居中
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
if "#memSearch {" not in s:
    s = s.replace("""/* 控制台滑块防溢出 */""",
"""#memSearch {
  position: fixed; left: 24px; top: 24px; z-index: 18; width: 230px;
  background: rgba(8,10,20,.85); border: 1px solid rgba(120,150,220,.3);
  border-radius: 12px; padding: 8px 10px; backdrop-filter: blur(8px);
}
#memSearchList { max-height: 180px; overflow: auto; margin-top: 6px; }

/* 控制台滑块防溢出 */""")
p.write_text(s, encoding="utf-8")
print("style.css 搜索面板样式已加")