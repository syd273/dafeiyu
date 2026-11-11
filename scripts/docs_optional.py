from pathlib import Path

# 1) .gitignore 排除第三方素材
p = Path(r"D:\大肥鱼\.gitignore")
s = p.read_text(encoding="utf-8")
if "milky-way-3d/room/" not in s:
    s = s.replace("milky-way-3d/memory_stars.json",
"""milky-way-3d/memory_stars.json
milky-way-3d/room/
milky-way-3d/cozy-room/
persona/stickers/
persona/stickers.json
persona/trends_cache.json""")
    p.write_text(s, encoding="utf-8")
    print(".gitignore 已更新")
else:
    print(".gitignore 已存在")

# 2) god.html 缺模型时提示安装
p = Path(r"D:\大肥鱼\milky-way-3d\god.html")
s = p.read_text(encoding="utf-8")
s = s.replace("""}, undefined, function (err) {
  document.getElementById('loading').textContent = '房间模型加载失败';
  console.error(err);
});""",
"""}, undefined, function (err) {
  document.getElementById('loading').innerHTML =
    '房间素材未安装<br><span style="font-size:10px;color:#4a567c">把 room.gltf 放到 milky-way-3d/room/ 即可（见 docs/可选组件.md）</span>';
  console.error(err);
});""")
p.write_text(s, encoding="utf-8")
print("god.html 缺模型提示已加")

# 3) README 加可选组件说明
p = Path(r"D:\大肥鱼\README.md")
s = p.read_text(encoding="utf-8")
if "可选组件" not in s:
    s = s.replace("## 开发文档", """## 可选组件（第三方素材，自行安装）

房间模型、表情包等第三方素材默认不随仓库发布，按需自行安装，见 [docs/可选组件.md](docs/可选组件.md)。

## 开发文档""")
    p.write_text(s, encoding="utf-8")
    print("README 已更新")