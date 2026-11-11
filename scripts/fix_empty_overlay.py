from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
# 空状态移到 List 之后（上层），避免被 List 透明区域拦截点击
s = s.replace("""        if (this.messages.length === 0) {
          this.emptyState()
        }
        List({ scroller: this.scroller }) {""",
"""        List({ scroller: this.scroller }) {""")
s = s.replace("""        .scrollBar(BarState.Off)
        .edgeEffect(EdgeEffect.None)
        .sticky(StickyStyle.Header)""",
"""        .scrollBar(BarState.Off)
        .edgeEffect(EdgeEffect.None)
        .sticky(StickyStyle.Header)

        if (this.messages.length === 0) {
          this.emptyState()
        }""")
p.write_text(s, encoding="utf-8")
print("empty state moved above list")