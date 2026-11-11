from pathlib import Path

# 1) index.html：控制台加重置按钮
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
if 'id="resetLook"' not in s:
    s = s.replace("""  <div class="stats"><span id="fps">— FPS</span><span id="starCount">…</span></div>""",
"""  <div class="stats"><span id="fps">— FPS</span><span id="starCount">…</span></div>
  <button id="resetLook">重置外观</button>""")
    p.write_text(s, encoding="utf-8")
    print("index.html 重置按钮已加")

# 2) main.js：保存初始视角 + 绑定重置
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
s = s.replace("""const controls = new OrbitControls(camera, renderer.domElement);""",
"""const controls = new OrbitControls(camera, renderer.domElement);""")
if "controls.saveState()" not in s:
    s = s.replace("""controls.enabled = false; // 开场动画期间禁用""",
"""controls.enabled = false; // 开场动画期间禁用
try { controls.saveState(); } catch (e) { }""")

if "resetLook" not in s:
    s = s.replace("""(function bindLookControls() {""",
"""(function bindResetLook() {
  const btn = document.getElementById('resetLook');
  if (!btn) return;
  btn.onclick = () => {
    try {
      const b = $('rngBloom'); if (b) { b.value = 0.95; bloom.strength = 0.95; }
      const t = $('rngTime'); if (t) { t.value = 1; timeScale = 1; }
      const s = $('rngStar'); if (s) { s.value = 1; applyStarBright(1); }
      const n = $('rngNebula'); if (n) { n.value = 1; applyNebula(1); }
      const sz = $('rngSize'); if (sz) { sz.value = 1; applyStarSize(1); }
      const sp = $('rngSpin'); if (sp) { sp.value = 1; controls.autoRotateSpeed = 0.22; }
      $('chkSpin').checked = true; spinOn = true;
      $('chkCruise').checked = true; controls.autoRotate = true;
      controls.reset();
      controls.update();
    } catch (e) { }
  };
})();

(function bindLookControls() {""")
    p.write_text(s, encoding="utf-8")
    print("main.js 重置逻辑已加")

# 3) style.css：重置按钮样式
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
if "#panel #resetLook" not in s:
    s += """
#panel #resetLook {
  width: 100%; margin-top: 8px; padding: 6px 0; border-radius: 8px;
  border: 1px solid rgba(150,170,230,.3); background: rgba(120,140,200,.12);
  color: #cfe0ff; font: 11px 'Microsoft YaHei'; cursor: pointer;
}
#panel #resetLook:active { background: rgba(120,140,200,.3); }
"""
    p.write_text(s, encoding="utf-8")
    print("style.css 按钮样式已加")