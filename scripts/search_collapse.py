from pathlib import Path

# 1) index.html：搜索面板加标题行与收起按钮 + 收起态胶囊按钮
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
s = s.replace("""  <div style="display:flex;align-items:center;gap:6px">
    <span style="color:#6f7fae;font-size:12px">🔍</span>
    <input id="memSearchInput" placeholder="查找记忆…" style="flex:1;background:transparent;border:0;outline:0;
      color:#dfe6ff;font:12px 'Microsoft YaHei'">
  </div>
  <div id="memSearchList" style="max-height:180px;overflow:auto;margin-top:6px"></div>""",
"""  <div style="display:flex;justify-content:space-between;align-items:center">
    <span style="color:#9fc1ff;font-size:12px;letter-spacing:1px">🔍 查找记忆</span>
    <span id="memSearchClose" style="cursor:pointer;color:#6f7fae;font-size:11px;padding:0 2px">收起 ×</span>
  </div>
  <div style="display:flex;align-items:center;gap:6px;margin-top:4px">
    <input id="memSearchInput" placeholder="输入关键词，如：阿东" style="flex:1;background:transparent;border:0;outline:0;
      color:#dfe6ff;font:12px 'Microsoft YaHei'">
  </div>
  <div id="memSearchList" style="max-height:120px;overflow:auto;margin-top:4px"></div>""")

# 收起态按钮（顶部居中）
s = s.replace("""<!-- 记忆搜索 -->""",
"""<!-- 查找记忆（收起态） -->
<button id="memSearchToggle" style="display:none;position:fixed;left:50%;transform:translateX(-50%);top:10px;z-index:18;
  padding:6px 14px;border-radius:999px;background:rgba(20,26,46,.85);color:#cfe0ff;
  border:1px solid rgba(120,150,220,.4);font:12px 'Microsoft YaHei';cursor:pointer;backdrop-filter:blur(6px)">🔍 查找记忆</button>

<!-- 记忆搜索 -->""")
p.write_text(s, encoding="utf-8")
print("index.html 收起按钮已加")

# 2) main.js 绑定
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
s = s.replace("""// 手机端：替换底部操作提示""",
"""// 查找记忆：收起 / 展开
(function () {
  const box = document.getElementById('memSearch');
  const toggle = document.getElementById('memSearchToggle');
  const close = document.getElementById('memSearchClose');
  if (box && toggle && close) {
    close.addEventListener('click', () => { box.style.display = 'none'; toggle.style.display = 'block'; });
    toggle.addEventListener('click', () => { box.style.display = 'block'; toggle.style.display = 'none'; });
  }
})();

// 手机端：替换底部操作提示""")
p.write_text(s, encoding="utf-8")
print("main.js 收起逻辑已加")