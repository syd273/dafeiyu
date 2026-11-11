from pathlib import Path
p = Path(r"D:\大肥鱼\anshiyu-server\life_core_client.py")
s = p.read_text(encoding="utf-8")
if "def get_options" not in s:
    s = s.replace('''    def consolidate(self) -> dict:
        return self._request("/consolidate", method="POST", data={})''',
'''    def consolidate(self) -> dict:
        return self._request("/consolidate", method="POST", data={})

    def get_options(self) -> dict:
        return self._request("/options")

    def set_options(self, payload: dict) -> dict:
        return self._request("/options", method="POST", data=payload or {})''')
    p.write_text(s, encoding="utf-8")
    print("已补 options 方法")
else:
    print("已存在")