from pathlib import Path

# 1) index.html：#memp 加标题行与 × 关闭
p = Path(r"D:\大肥鱼\milky-way-3d\index.html")
s = p.read_text(encoding="utf-8")
s = s.replace("""<div id="memp" style="display:none;position:fixed;right:22px;top:110px;width:340px;max-height:60vh;overflow:auto;z-index:20;
  background:rgba(8,10,20,.92);border:1px solid rgba(120,150,220,.35);border-radius:14px;padding:16px;
  color:#dfe6ff;font:13px/1.7 'Microsoft YaHei',sans-serif;backdrop-filter:blur(10px);box-shadow:0 8px 30px rgba(0,0,0,.6)">
  <div id="memp-meta" style="color:#8fa2d8;font-size:12px;margin-bottom:10px"></div>""",
"""<div id="memp" style="display:none;position:fixed;right:22px;top:110px;width:340px;max-height:60vh;overflow:auto;z-index:20;
  background:rgba(8,10,20,.92);border:1px solid rgba(120,150,220,.35);border-radius:14px;padding:16px;
  color:#dfe6ff;font:13px/1.7 'Microsoft YaHei',sans-serif;backdrop-filter:blur(10px);box-shadow:0 8px 30px rgba(0,0,0,.6)">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="color:#9fc1ff;font-size:12px;letter-spacing:1px">记忆详情</span>
    <span id="memp-close" style="cursor:pointer;color:#9db4ef;font-size:18px;line-height:1;padding:0 4px">×</span>
  </div>
  <div id="memp-meta" style="color:#8fa2d8;font-size:12px;margin-bottom:10px"></div>""")
p.write_text(s, encoding="utf-8")
print("index.html 详情关闭按钮已加")

# 2) main.js 绑定关闭
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
s = s.replace("""// 查找记忆：收起 / 展开""",
"""// 记忆详情：× 关闭
(function () {
  const box = document.getElementById('memp');
  const close = document.getElementById('memp-close');
  if (box && close) {
    close.addEventListener('click', (ev) => {
      ev.stopPropagation();
      box.style.display = 'none';
      selectedMem = null;
    });
  }
})();

// 查找记忆：收起 / 展开""")
p.write_text(s, encoding="utf-8")
print("main.js 关闭逻辑已加")