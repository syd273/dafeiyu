from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
if "collapseByDefault" not in s:
    s = s.replace("""// 手机端：替换底部操作提示""",
"""// 进入星图默认收起：查找记忆、控制台（只保留左侧她的此刻）
(function collapseByDefault() {
  const box = document.getElementById('memSearch');
  const toggle = document.getElementById('memSearchToggle');
  const panel = document.getElementById('panel');
  const panelToggle = document.getElementById('panelToggle');
  if (box && toggle) { box.style.display = 'none'; toggle.style.display = 'block'; }
  if (panel && panelToggle) { panel.style.display = 'none'; panelToggle.style.display = 'block'; }
})();

// 手机端：替换底部操作提示""")
    p.write_text(s, encoding="utf-8")
    print("默认收起已加")