from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")

# 搜索面板：顶部居中，不再遮返回和左面板
s = s.replace("""  #memSearch {
    left: max(10px, env(safe-area-inset-left));
    top: max(8px, env(safe-area-inset-top));
    width: 200px; padding: 6px 8px;
  }
  #memSearchList { max-height: 140px; }""",
"""  #memSearch {
    left: 50%; transform: translateX(-50%);
    top: max(8px, env(safe-area-inset-top));
    width: 300px; padding: 6px 10px;
  }
  #memSearchList { max-height: 150px; }""")

# 滑块不再溢出
s += """
/* 控制台滑块防溢出 */
#panel .row { min-width: 0; }
#panel .row span { flex: none; }
#panel input[type=range] { width: 100%; min-width: 0; flex: 1; }
"""
p.write_text(s, encoding="utf-8")
print("CSS 已修")