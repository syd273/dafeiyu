from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\style.css")
s = p.read_text(encoding="utf-8")
extra = """

/* 手机横屏：搜索面板强制居中（最高优先级） */
@media (max-height: 700px) {
  #memSearch {
    left: 50% !important;
    transform: translateX(-50%) !important;
    top: max(8px, env(safe-area-inset-top)) !important;
    width: 300px !important;
    padding: 6px 10px !important;
  }
  #memSearchList { max-height: 150px !important; }
}
"""
if "强制居中" not in s:
    s += extra
    p.write_text(s, encoding="utf-8")
    print("强制居中已加")