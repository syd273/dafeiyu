from pathlib import Path

# ===== index.html =====
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")

# 左侧面板标题加收起
s = s.replace("""  <div style="color:#9fc1ff;font-size:12px;letter-spacing:2px;margin-bottom:6px">安诗鱼 · 此刻</div>""",
"""  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
    <span style="color:#9fc1ff;font-size:12px;letter-spacing:2px">安诗鱼 · 此刻</span>
    <span id="life-close" style="cursor:pointer;color:#6f7fae;font-size:11px;padding:0 2px">收起 ‹</span>
  </div>""")

# 左侧展开按钮（默认隐藏）
s = s.replace("""<!-- 加载屏 -->""",
"""<!-- 侧栏展开按钮 -->
<button id="lifeToggle" style="display:none;position:fixed;left:24px;bottom:96px;z-index:17;padding:8px 14px;border-radius:999px;
  background:rgba(20,26,46,.85);color:#cfe0ff;border:1px solid rgba(120,150,220,.4);
  font:12px 'Microsoft YaHei';cursor:pointer;backdrop-filter:blur(6px)">她的此刻 ›</button>

<!-- 加载屏 -->""")

# 右侧控制台标题加收起
s = s.replace("""  <div class="p-title">控制台 <span>CONTROL</span></div>""",
"""  <div class="p-title" style="display:flex;justify-content:space-between;align-items:center">
    <span>控制台 <span>CONTROL</span></span>
    <span id="panel-close" style="cursor:pointer;color:#6f7fae;font-size:11px;letter-spacing:0">收起 ›</span>
  </div>""")

# 右侧展开按钮
s = s.replace("""<!-- 侧栏展开按钮 -->""",
"""<!-- 控制台展开按钮 -->
<button id="panelToggle" style="display:none;position:fixed;right:34px;top:34px;z-index:17;padding:8px 14px;border-radius:999px;
  background:rgba(20,26,46,.85);color:#cfe0ff;border:1px solid rgba(120,150,220,.4);
  font:12px 'Microsoft YaHei';cursor:pointer;backdrop-filter:blur(6px)">控制台 ‹</button>

<!-- 侧栏展开按钮 -->""")
p.write_text(s, encoding="utf-8")
print("index.html 已加收起按钮")

# ===== main.js =====
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
s = s.replace("""// 手机端：替换底部操作提示""",
"""// 侧栏收起 / 展开
(function () {
  const life = document.getElementById('life');
  const lifeToggle = document.getElementById('lifeToggle');
  const panel = document.getElementById('panel');
  const panelToggle = document.getElementById('panelToggle');
  const lifeClose = document.getElementById('life-close');
  const panelClose = document.getElementById('panel-close');
  if (lifeClose && life && lifeToggle) {
    lifeClose.addEventListener('click', () => { life.style.display = 'none'; lifeToggle.style.display = 'block'; });
    lifeToggle.addEventListener('click', () => { life.style.display = 'block'; lifeToggle.style.display = 'none'; });
  }
  if (panelClose && panel && panelToggle) {
    panelClose.addEventListener('click', () => { panel.style.display = 'none'; panelToggle.style.display = 'block'; });
    panelToggle.addEventListener('click', () => { panel.style.display = ''; panelToggle.style.display = 'none'; });
  }
})();

// 手机端：替换底部操作提示""")
p.write_text(s, encoding="utf-8")
print("main.js 已加收起逻辑")

# ===== style.css 横屏适配 =====
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
s = s.replace("""  #memp {
    right: max(10px, env(safe-area-inset-right));""",
"""  #lifeToggle {
    left: max(10px, env(safe-area-inset-left));
    bottom: max(10px, env(safe-area-inset-bottom));
    padding: 6px 12px; font-size: 11px;
  }
  #panelToggle {
    top: max(8px, env(safe-area-inset-top));
    right: max(10px, env(safe-area-inset-right));
    padding: 6px 12px; font-size: 11px;
  }
  #memp {
    right: max(10px, env(safe-area-inset-right));""")
p.write_text(s, encoding="utf-8")
print("style.css 已适配")