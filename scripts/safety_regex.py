from pathlib import Path
p = Path(r"D:\大肥鱼\persona\safety.py")
s = p.read_text(encoding="utf-8")
if "PRIVACY_PATTERNS" not in s:
    s = s.replace('''# 她回复命中时的替换话术''',
'''# 隐私侵犯类正则（容忍中间插字）
PRIVACY_PATTERNS = [
    r"查.{0,8}身份证", r"身份证.{0,6}(号|信息|地址)",
    r"查.{0,8}银行卡", r"银行卡.{0,6}号",
    r"查.{0,8}手机号", r"查.{0,8}住址", r"查.{0,8}开房",
    r"人肉", r"开盒", r"盗.{0,6}密码", r"破解.{0,6}密码",
    r"窃听", r"定位.{0,6}(别人|他|她)",
]

# 她回复命中时的替换话术''')
    s = s.replace('''def check(text: str) -> dict:
    """检查文本，返回 {hit, category, word}"""
    t = str(text or "")
    if not t.strip():
        return {"hit": False}
    custom = _load_custom()
    for w in FORBIDDEN + custom.get("forbidden", []):
        if w and w in t:
            return {"hit": True, "category": "forbidden", "word": w}
    for w in PRIVACY + custom.get("privacy", []):
        if w and w in t:
            return {"hit": True, "category": "privacy", "word": w}
    return {"hit": False}''',
'''def check(text: str) -> dict:
    """检查文本，返回 {hit, category, word}"""
    t = str(text or "")
    if not t.strip():
        return {"hit": False}
    custom = _load_custom()
    for w in FORBIDDEN + custom.get("forbidden", []):
        if w and w in t:
            return {"hit": True, "category": "forbidden", "word": w}
    for w in PRIVACY + custom.get("privacy", []):
        if w and w in t:
            return {"hit": True, "category": "privacy", "word": w}
    for pat in PRIVACY_PATTERNS:
        if re.search(pat, t):
            return {"hit": True, "category": "privacy", "word": pat}
    return {"hit": False}''')
    p.write_text(s, encoding="utf-8")
    print("隐私正则已加")