from pathlib import Path

# 1) index.html 控制台加 4 个滑块
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
if 'id="rngStar"' not in s:
    s = s.replace("""  <div class="row"><span>时流</span><input type="range" id="rngTime" min="0" max="5" step="0.1" value="1"></div>""",
"""  <div class="row"><span>时流</span><input type="range" id="rngTime" min="0" max="5" step="0.1" value="1"></div>
  <div class="row"><span>星光</span><input type="range" id="rngStar" min="0.3" max="1.8" step="0.05" value="1"></div>
  <div class="row"><span>星云</span><input type="range" id="rngNebula" min="0" max="2.5" step="0.05" value="1"></div>
  <div class="row"><span>星点</span><input type="range" id="rngSize" min="0.5" max="2" step="0.05" value="1"></div>
  <div class="row"><span>转速</span><input type="range" id="rngSpin" min="0" max="3" step="0.1" value="1"></div>""")
    p.write_text(s, encoding="utf-8")
    print("index.html 滑块已加")

# 2) main.js 绑定调节
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
if "rngStar" not in s:
    s = s.replace("""addEventListener('resize', () => {""",
"""/* ---------- 星图外观调节 ---------- */
function applyStarBright(v) {
  try {
    starMat.uniforms.uOpacity.value = 0.86 * v;
    brightMat.uniforms.uOpacity.value = 0.74 * v;
    if (bgMat) bgMat.uniforms.uOpacity.value = 0.55 * v;
    if (memMat) memMat.uniforms.uOpacity.value = 0.86 * v;
  } catch (e) { }
}

function applyNebula(v) {
  try {
    for (const sp of nebGroup.children) {
      sp.material.opacity = sp.userData.base * v;
    }
    dustMat.uniforms.uOpacity.value = 0.12 * v;
    hazeMat.uniforms.uOpacity.value = 0.055 * v;
  } catch (e) { }
}

function applyStarSize(v) {
  try {
    const px = pxValue() * v;
    for (const m of [starMat, brightMat, hazeMat, dustMat]) m.uniforms.uPx.value = px;
    if (memMat) memMat.uniforms.uPx.value = px;
  } catch (e) { }
}

(function bindLookControls() {
  const star = $('rngStar'), neb = $('rngNebula'), size = $('rngSize'), spin = $('rngSpin');
  if (star) star.oninput = e => applyStarBright(parseFloat(e.target.value));
  if (neb) neb.oninput = e => applyNebula(parseFloat(e.target.value));
  if (size) size.oninput = e => applyStarSize(parseFloat(e.target.value));
  if (spin) spin.oninput = e => { controls.autoRotateSpeed = 0.22 * parseFloat(e.target.value); };
})();

addEventListener('resize', () => {""")
    p.write_text(s, encoding="utf-8")
    print("main.js 调节已加")

# 3) style.css 横屏控制台可滚动
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
s = s.replace("""    width: 176px; padding: 10px 12px 8px;
  }""",
"""    width: 176px; padding: 10px 12px 8px;
    max-height: calc(100vh - 16px); overflow: auto;
  }""")
p.write_text(s, encoding="utf-8")
print("style.css 控制台可滚动")