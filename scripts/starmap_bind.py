from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\server.py")
s = p.read_text(encoding="utf-8")
if "bind=" not in s:
    s = s.replace("port=8899)", "port=8899, bind='0.0.0.0')")
    p.write_text(s, encoding="utf-8")
    print("bind 0.0.0.0 已加")
else:
    print("已存在 bind")