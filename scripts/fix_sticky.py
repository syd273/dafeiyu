from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""            }
            .sticky(StickyStyle.Header)
          }, (g: MsgGroup) => g.dateKey)""",
"""            }
          }, (g: MsgGroup) => g.dateKey)""")
p.write_text(s, encoding="utf-8")
print("fixed")