from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\MemoryRecords.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""  confirmDelete(item: MemItem) {
    AlertDialog.show({
      title: '删除记忆',
      message: `确定删除第 ${item.index} 颗星对应的记忆吗？删除后星图上也会消失。`,
      primaryButton: {
        value: '取消',
        action: () => { },
      },
      secondaryButton: {
        value: '删除',
        fontColor: '#ff6b6b',
        action: () => { this.remove(item); },
      },
    });
  }""",
"""  confirmDelete(item: MemItem) {
    // 直接删除（按钮已明确标注）
    this.remove(item);
  }""")
p.write_text(s, encoding="utf-8")
print("改为直接删除")