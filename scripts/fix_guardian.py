from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\scripts\guardian.py")
s = p.read_text(encoding="utf-8")
s = s.replace('        c = sqlite3.connect(BASE / "memory" / "archive.db")', '        conn = sqlite3.connect(BASE / "memory" / "archive.db")')
s = s.replace('        n_msg = c.execute("SELECT COUNT(*) FROM messages WHERE ts>=?", (start,)).fetchone()[0]', '        n_msg = conn.execute("SELECT COUNT(*) FROM messages WHERE ts>=?", (start,)).fetchone()[0]')
s = s.replace("        n_user = c.execute(\"SELECT COUNT(*) FROM messages WHERE ts>=? AND role='user'\", (start,)).fetchone()[0]", "        n_user = conn.execute(\"SELECT COUNT(*) FROM messages WHERE ts>=? AND role='user'\", (start,)).fetchone()[0]")
s = s.replace('        c.close()', '        conn.close()')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("fixed")