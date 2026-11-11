from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# 1) 缓存分组列表
s = s.replace("  @State messages: ChatMsg[] = [];",
"""  @State messages: ChatMsg[] = [];
  @State groupList: MsgGroup[] = [];""")

# 2) addMessage 后重建分组
s = s.replace("""    this.messages.push({ role: role, text: text, ts: Date.now() });
    this.scrollBottom();""",
"""    this.messages.push({ role: role, text: text, ts: Date.now() });
    this.rebuildGroups();
    this.scrollBottom();""")

# 3) 新增 rebuildGroups（groups() 之后）
s = s.replace("""  showTime(index: number, items: ChatMsg[]): boolean {""",
"""  rebuildGroups() {
    this.groupList = this.groups();
  }

  showTime(index: number, items: ChatMsg[]): boolean {""")

# 4) build 使用缓存 + 修正外层 key（含最后一条时间戳，保证新消息重建）
s = s.replace("""        List({ scroller: this.scroller }) {
          ForEach(this.groups(), (g: MsgGroup) => {""",
"""        List({ scroller: this.scroller }) {
          ForEach(this.groupList, (g: MsgGroup) => {""")
s = s.replace("""          }, (g: MsgGroup) => g.dateKey)""",
"""          }, (g: MsgGroup) => `${g.dateKey}_${g.items.length}_${g.items[g.items.length - 1].ts}`)""")

# 5) 删除消息后重建
s = s.replace("""      MenuItem({ content: '删除' }).onClick(() => {
        this.messages.splice(idx, 1);
      })""",
"""      MenuItem({ content: '删除' }).onClick(() => {
        this.messages.splice(idx, 1);
        this.rebuildGroups();
      })""")

# 6) 性能：移除毛玻璃、简化入场动画、去掉弹簧边缘
s = s.replace("""      .backgroundColor(this.bgKey === 'default' ? '#11151fE6' : '#11151fCC')
      .backdropBlur(16)""",
"""      .backgroundColor('#11151f')""")
s = s.replace("""                .transition(TransitionEffect.OPACITY
                  .combine(TransitionEffect.scale({ x: 0.94, y: 0.94 }))
                  .combine(TransitionEffect.translate({ y: 10 })))""",
"""                .transition(TransitionEffect.OPACITY)""")
s = s.replace("""        .scrollBar(BarState.Off)
        .edgeEffect(EdgeEffect.Spring)
        .sticky(StickyStyle.Header)""",
"""        .scrollBar(BarState.Off)
        .edgeEffect(EdgeEffect.None)
        .sticky(StickyStyle.Header)""")

# 7) 气泡阴影减轻
s = s.replace(".shadow({ radius: 8, color: '#40000000', offsetY: 2 })", ".shadow({ radius: 4, color: '#33000000', offsetY: 1 })")
s = s.replace(".shadow({ radius: 8, color: '#33000000', offsetY: 2 })", ".shadow({ radius: 4, color: '#26000000', offsetY: 1 })")

p.write_text(s, encoding="utf-8")
print("fixed display + performance")