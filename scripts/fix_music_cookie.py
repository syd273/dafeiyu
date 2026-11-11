from pathlib import Path
p = Path(r"D:\大肥鱼\persona\music.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",''',
'''    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",''')
s = s.replace('''        try:
            s = requests.Session()
            s.trust_env = False
            r = s.get(u, headers=HEADERS, timeout=20)''',
'''        try:
            s = requests.Session()
            s.trust_env = False
            # 先访问首页拿 buvid cookie，否则排行接口会风控（-352）
            try:
                s.get("https://www.bilibili.com/", headers=HEADERS, timeout=15)
            except Exception:
                pass
            r = s.get(u, headers=HEADERS, timeout=20)''')
p.write_text(s, encoding="utf-8")
print("music.py 已修复")