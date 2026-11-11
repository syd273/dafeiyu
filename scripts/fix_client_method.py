from pathlib import Path
p = Path(r"D:\大肥鱼\anshiyu-server\life_core_client.py")
s = p.read_text(encoding="utf-8")
s = s.replace('return self._req("GET", "/options")', 'return self._request("/options")')
s = s.replace('return self._req("POST", "/options", payload)', 'return self._request("/options", method="POST", data=payload)')
p.write_text(s, encoding="utf-8")
print("已修复")