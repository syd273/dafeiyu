from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
old = """  #hints { display: none; }"""
new = """  #hints {
    display: flex; bottom: max(4px, env(safe-area-inset-bottom));
    font-size: 9.5px; gap: 10px; padding: 3px 10px; letter-spacing: .04em;
    background: rgba(6,8,16,.35); border-radius: 10px;
  }
  #hints kbd { font-size: 8.5px; padding: 0 3px; }
  #hints .sep { display: none; }"""
s = s.replace(old, new)
s = s.replace("    width: 246px; padding: 10px 12px; font-size: 11.5px;",
              "    width: 236px; padding: 10px 12px; font-size: 11.5px;")
p.write_text(s, encoding="utf-8")
print("横屏提示已调整")