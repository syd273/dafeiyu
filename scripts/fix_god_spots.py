# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"D:\大肥鱼\milky-way-3d\god.html")
s = p.read_text(encoding="utf-8")

s = s.replace("""var ROOM_SPOTS = {
  '客厅': [0.05, 0.12],
  '厨房': [0.28, -0.18],
  '阳台': [-0.30, -0.10],
  '卧室': [-0.28, 0.22],
  '家': [0.0, 0.05],
};""",
"""var ROOM_SPOTS = {
  '客厅': [0.0, 0.2],
  '厨房': [0.26, -0.08],
  '阳台': [-0.12, -0.28],
  '卧室': [-0.24, 0.22],
  '家': [0.0, 0.05],
};""")

s = s.replace("""  var maxDim = Math.max(roomSize.x, roomSize.y, roomSize.z);
  herSprite.position.x = spot[0] * roomSize.x;
  herSprite.position.z = spot[1] * roomSize.z;
  herSprite.position.y = roomSize.y * 0.35;""",
"""  herSprite.position.x = spot[0] * roomSize.x;
  herSprite.position.z = spot[1] * roomSize.z;
  herSprite.position.y = roomSize.y * 0.12;""")

p.write_text(s, encoding="utf-8")
print("位置已调整")
