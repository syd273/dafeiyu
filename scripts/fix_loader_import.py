# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"D:\大肥鱼\milky-way-3d\lib\GLTFLoader.js")
s = p.read_text(encoding="utf-8")
s = s.replace("'../utils/BufferGeometryUtils.js'", "'./BufferGeometryUtils.js'")
p.write_text(s, encoding="utf-8")
print("路径已改")
