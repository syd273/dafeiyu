from pathlib import Path

# ===== index.html：记忆搜索面板 =====
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
if 'id="memSearch"' not in s:
    s = s.replace("""<!-- 侧栏展开按钮 -->""",
"""<!-- 记忆搜索 -->
<div id="memSearch" style="position:fixed;left:24px;top:24px;z-index:18;width:230px;
  background:rgba(8,10,20,.85);border:1px solid rgba(120,150,220,.3);border-radius:12px;
  padding:8px 10px;backdrop-filter:blur(8px)">
  <div style="display:flex;align-items:center;gap:6px">
    <span style="color:#6f7fae;font-size:12px">🔍</span>
    <input id="memSearchInput" placeholder="查找记忆…" style="flex:1;background:transparent;border:0;outline:0;
      color:#dfe6ff;font:12px 'Microsoft YaHei'">
  </div>
  <div id="memSearchList" style="max-height:180px;overflow:auto;margin-top:6px"></div>
</div>

<!-- 侧栏展开按钮 -->""")
    p.write_text(s, encoding="utf-8")
    print("index.html 搜索框已加")

# ===== main.js：搜索 + 定位 + 点击容差 =====
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")

# 1) 点击星星：先按屏幕距离找最近星（更准），再 raycast
s = s.replace("""  memRay.setFromCamera(mouse, camera);
  const hits = memRay.intersectObject(memPoints, false);
  if (hits.length) {""",
"""  // 先按屏幕距离找最近星（手机上点小点更准）
  {
    let near = -1, best = 30;
    for (let i = 0; i < memData.length; i++) {
      const sc = window.__memScreen(i);
      if (sc[2] > 1) continue;
      const d = Math.hypot(ev.clientX - sc[0], ev.clientY - sc[1]);
      if (d < best) { best = d; near = i; }
    }
    if (near >= 0) { window.__showMem(near); return; }
  }
  memRay.setFromCamera(mouse, camera);
  const hits = memRay.intersectObject(memPoints, false);
  if (hits.length) {""")

# 2) 记忆面板显示 + 搜索定位（插在点击处理之后）
s = s.replace("""/* ---------- 她的生活面板 ---------- */""",
"""/* ---------- 记忆详情 / 搜索定位 ---------- */
window.__showMem = function (i) {
  if (!memData || !memData[i]) return;
  selectedMem = i;
  const m = memData[i];
  memMeta.textContent = '第 ' + (i + 1) + ' 颗星 · ' + new Date(m.ts * 1000).toLocaleString('zh-CN')
    + ' · ' + m.emo;
  memText.textContent = m.view || m.text;
  memPanel.style.display = 'block';
};

window.__focusMem = function (i) {
  if (!memData || !memData[i] || !memPoints) return;
  const a = memPoints.geometry.getAttribute('position');
  const pos = new THREE.Vector3(a.getX(i), a.getY(i), a.getZ(i));
  memPoints.localToWorld(pos);
  const dir = camera.position.clone().sub(pos);
  if (dir.lengthSq() < 1e-6) dir.set(0, 0, 1);
  dir.normalize();
  controls.target.copy(pos);
  camera.position.copy(pos.clone().add(dir.multiplyScalar(45)));
  controls.update();
  window.__showMem(i);
};

(function () {
  const input = document.getElementById('memSearchInput');
  const list = document.getElementById('memSearchList');
  if (!input || !list) return;
  function render(q) {
    const data = window.__memData || [];
    const hits = [];
    for (let i = 0; i < data.length && hits.length < 25; i++) {
      const t = (data[i].view || data[i].text || '');
      if (!q || t.indexOf(q) >= 0) hits.push({ i: i, t: t });
    }
    list.innerHTML = hits.map(h =>
      '<div data-i="' + h.i + '" style="padding:6px 4px;border-bottom:1px solid #1a2236;cursor:pointer;'
      + 'font-size:11px;line-height:1.5;color:#cfe0ff">'
      + '<span style="color:#ffd48a">第' + (h.i + 1) + '颗</span> '
      + h.t.slice(0, 32) + (h.t.length > 32 ? '…' : '') + '</div>'
    ).join('') || '<div style="color:#5f6c96;font-size:11px;padding:6px">没有找到</div>';
    list.querySelectorAll('[data-i]').forEach(el => {
      el.onclick = () => { window.__focusMem(parseInt(el.getAttribute('data-i'), 10)); };
    });
  }
  input.addEventListener('input', () => render(input.value.trim()));
  // 等记忆加载完成后初始化列表
  const timer = setInterval(() => {
    if (window.__memData && window.__memData.length) { render(''); clearInterval(timer); }
  }, 700);
  setTimeout(() => clearInterval(timer), 30000);
})();

/* ---------- 她的生活面板 ---------- */""")
p.write_text(s, encoding="utf-8")
print("main.js 搜索与点击已加")

# ===== style.css 横屏适配搜索框 =====
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
s = s.replace("""  #lifeToggle {""",
"""  #memSearch {
    left: max(10px, env(safe-area-inset-left));
    top: max(8px, env(safe-area-inset-top));
    width: 200px; padding: 6px 8px;
  }
  #memSearchList { max-height: 140px; }
  #lifeToggle {""")
p.write_text(s, encoding="utf-8")
print("style.css 搜索框适配")