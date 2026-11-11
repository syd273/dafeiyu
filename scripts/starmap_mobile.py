from pathlib import Path

# 1) style.css 追加手机横屏媒体查询
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
extra = """

/* ===== 手机横屏优化（由安诗鱼 App 使用） ===== */
@media (max-height: 620px) {
  #title { display: none; }
  #panel {
    top: max(8px, env(safe-area-inset-top));
    right: max(10px, env(safe-area-inset-right));
    width: 176px; padding: 10px 12px 8px;
  }
  #panel .p-title { font-size: 11px; padding-bottom: 6px; margin-bottom: 6px; }
  #panel label.ck { font-size: 11px; gap: 8px; }
  #panel .row { font-size: 11px; padding-top: 4px; gap: 8px; }
  #panel .row span { width: 26px; }
  #panel .stats { font-size: 9.5px; }
  #hints { display: none; }
  #life {
    left: max(10px, env(safe-area-inset-left));
    bottom: max(10px, env(safe-area-inset-bottom));
    width: 246px; padding: 10px 12px; font-size: 11.5px;
    max-height: 44vh; overflow: auto;
  }
  #life #life-feed { font-size: 11px; }
  #tlBtn {
    right: max(10px, env(safe-area-inset-right));
    bottom: max(10px, env(safe-area-inset-bottom));
    padding: 6px 12px; font-size: 11px;
  }
  #tlPanel {
    right: max(10px, env(safe-area-inset-right));
    top: max(8px, env(safe-area-inset-top));
    width: 300px; max-height: 70vh; overflow: auto; padding: 10px 12px;
  }
  #memp {
    right: max(10px, env(safe-area-inset-right));
    top: max(8px, env(safe-area-inset-top));
    width: 300px; max-height: 70vh; font-size: 12px;
  }
  #loading p { font-size: 11px; letter-spacing: .2em; }
}
"""
if "手机横屏优化" not in s:
    s += extra
    p.write_text(s, encoding="utf-8")
    print("style.css 手机横屏优化已加")

# 2) main.js 触摸设备提示文案
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
if "单指" not in s:
    s = s.replace("""addEventListener('resize', () => {""",
"""// 手机端：替换底部操作提示
if ('ontouchstart' in window) {
  const h = document.getElementById('hints');
  if (h) {
    h.innerHTML = '<span>单指 <em>旋转</em></span><span>双指 <em>缩放/平移</em></span>'
      + '<span class="sep"></span><span>点击星星 <em>查看记忆</em></span>';
  }
}

addEventListener('resize', () => {""", 1)
    p.write_text(s, encoding="utf-8")
    print("main.js 触摸提示已加")

# 3) App 星图全屏横屏
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\StarMap.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""  aboutToAppear() {
    this.setOrientation(window.Orientation.LANDSCAPE);
    this.loadUrl();
  }

  aboutToDisappear() {
    this.setOrientation(window.Orientation.PORTRAIT);
  }""",
"""  aboutToAppear() {
    this.enterFullscreen();
    this.setOrientation(window.Orientation.LANDSCAPE);
    this.loadUrl();
  }

  aboutToDisappear() {
    this.setOrientation(window.Orientation.PORTRAIT);
    this.exitFullscreen();
  }

  async enterFullscreen() {
    try {
      const win = await window.getLastWindow(getContext(this));
      await win.setWindowLayoutFullScreen(true);
      await win.setWindowSystemBarEnable([]);
    } catch (e) { }
  }

  async exitFullscreen() {
    try {
      const win = await window.getLastWindow(getContext(this));
      await win.setWindowLayoutFullScreen(false);
      await win.setWindowSystemBarEnable(['status', 'navigation']);
    } catch (e) { }
  }""")
p.write_text(s, encoding="utf-8")
print("StarMap 全屏已加")