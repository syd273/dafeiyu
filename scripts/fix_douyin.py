from pathlib import Path
p = Path(r"D:\大肥鱼\persona\douyin.py")
s = p.read_text(encoding="utf-8")
s = s.replace('        words = ((data.get("data") or {}).get("word_list") or [])',
              '        words = data.get("word_list") or ((data.get("data") or {}).get("word_list") or [])')
p.write_text(s, encoding="utf-8")
print("fixed")