# -*- coding: utf-8 -*-
from pathlib import Path

# 1) god.html：开关检查 + 降级
p = Path(r"D:\大肥鱼\milky-way-3d\god.html")
s = p.read_text(encoding="utf-8")

s = s.replace("""var room = null, roomBox = null, roomSize = null;
var loader = new GLTFLoader();
loader.load('room/room.gltf', function (gltf) {""",
"""var room = null, roomBox = null, roomSize = null;

function startRoom() {
var loader = new GLTFLoader();
loader.load('room/room.gltf', function (gltf) {""")

s = s.replace("""}, undefined, function (err) {
  document.getElementById('loading').innerHTML =
    '房间素材未安装<br><span style="font-size:10px;color:#4a567c">把 room.gltf 放到 milky-way-3d/room/ 即可（见 docs/可选组件.md）</span>';
  console.error(err);
});""",
"""}, undefined, function (err) {
  document.getElementById('loading').innerHTML =
    '房间素材未安装<br><span style="font-size:10px;color:#4a567c">把 room.gltf 放到 milky-way-3d/room/ 即可（见 docs/可选组件.md）</span>';
  console.error(err);
});
}

// 功能开关：房间展示可关闭
fetch('http://' + location.hostname + ':8900/api/features?token=anshiyu-app-2026', { cache: 'no-store' })
  .then(function (r) { return r.json(); })
  .then(function (f) {
    if (f && f.room === false) {
      document.getElementById('loading').innerHTML =
        '房间展示已关闭<br><span style="font-size:10px;color:#4a567c">在 App 设置 → 功能开关 里可以开启</span>';
      return;
    }
    startRoom();
  })
  .catch(function () { startRoom(); });""")

p.write_text(s, encoding="utf-8")
print("god.html 开关已加")
