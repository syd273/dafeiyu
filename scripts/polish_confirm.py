from pathlib import Path

# 1) MemoryRecords：删除二次确认
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\MemoryRecords.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  @State fromCache: boolean = false;",
              "  @State fromCache: boolean = false;\n  @State pendingDelete: number = -1;")
s = s.replace("""                  Text('删除')
                    .fontSize(11).fontColor('#ff6b6b')
                    .padding({ left: 8, right: 4, top: 2, bottom: 2 })
                    .onClick(() => { this.remove(it); })""",
"""                  Text(this.pendingDelete === it.id ? '确认删除？' : '删除')
                    .fontSize(11)
                    .fontColor(this.pendingDelete === it.id ? '#ff3b3b' : '#ff6b6b')
                    .padding({ left: 8, right: 4, top: 2, bottom: 2 })
                    .onClick(() => {
                      if (this.pendingDelete === it.id) {
                        this.pendingDelete = -1;
                        this.remove(it);
                      } else {
                        this.pendingDelete = it.id;
                        this.tip = '再点一次「确认删除」才会删除';
                      }
                    })""")
p.write_text(s, encoding="utf-8")
print("记忆删除二次确认已加")

# 2) TopBar：加刷新（重连）
p = Path(r"D:\anshiyu_app\entry\src\main\ets\components\TopBar.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("  onStar: () => void = () => { };",
              "  onStar: () => void = () => { };\n  onRefresh: () => void = () => { };")
s = s.replace("""      Text('⭐')""",
"""      Text(this.online ? '' : '重连')
        .fontSize(12).fontColor('#ffd48a')
        .padding({ left: 8, right: 8 })
        .onClick(() => { this.onRefresh(); })
      Text('⭐')""")
p.write_text(s, encoding="utf-8")
print("TopBar 重连已加")

# 3) Index 传 onRefresh
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("          onStar: () => { router.pushUrl({ url: 'pages/StarMap' }); },",
"""          onStar: () => { router.pushUrl({ url: 'pages/StarMap' }); },
          onRefresh: () => { this.loadConfig().then(() => { this.loadStatus(); this.connectWs(); }); },""")
p.write_text(s, encoding="utf-8")
print("Index 重连已加")