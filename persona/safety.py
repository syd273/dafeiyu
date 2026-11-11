# -*- coding: utf-8 -*-
"""内容安全：违法类 / 隐私类词库过滤

规则：
- 用户输入命中「违法/危害」类 → 拒绝回复（不调用模型）
- 用户输入命中「隐私侵犯」类 → 拒绝
- 她生成的回复命中 → 替换成安全话术
- 词库可扩展：memory/safety_words.json（追加后重启生效）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
CUSTOM = BASE.parent / "memory" / "safety_words.json"

# 违法 / 危害类（命中即拒绝）
FORBIDDEN = [
    "赌博", "赌场", "开盘口", "毒品", "冰毒", "海洛因", "大麻", "摇头丸",
    "枪支", "买枪", "弹药", "炸药", "炸弹", "爆炸物", "自制炸弹",
    "色情", "裸聊", "卖淫", "嫖娼", "性交易", "迷药", "偷拍",
    "诈骗", "洗钱", "人肉", "开盒", "查户籍", "黑客攻击", "盗号",
    "恐怖袭击", "绑架", "杀人", "自杀方法", "教唆自杀",
]

# 隐私侵犯类（命中即拒绝）
PRIVACY = [
    "查身份证", "查银行卡", "查手机号", "查住址", "查开房",
    "人肉搜索", "开盒", "查通话记录", "查聊天记录", "盗取密码",
    "帮我破解", "窃听", "定位别人",
]

# 隐私侵犯类正则（容忍中间插字）
PRIVACY_PATTERNS = [
    r"查.{0,8}身份证", r"身份证.{0,6}(号|信息|地址)",
    r"查.{0,8}银行卡", r"银行卡.{0,6}号",
    r"查.{0,8}手机号", r"查.{0,8}住址", r"查.{0,8}开房",
    r"人肉", r"开盒", r"盗.{0,6}密码", r"破解.{0,6}密码",
    r"窃听", r"定位.{0,6}(别人|他|她)",
]

# 她回复命中时的替换话术
SAFE_REPLY = "这个话题我不太想聊，换个轻松点的吧。"


def _load_custom() -> dict:
    try:
        d = json.loads(CUSTOM.read_text(encoding="utf-8"))
        return {
            "forbidden": [str(x) for x in (d.get("forbidden") or [])],
            "privacy": [str(x) for x in (d.get("privacy") or [])],
        }
    except Exception:
        return {"forbidden": [], "privacy": []}


def check(text: str) -> dict:
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
    return {"hit": False}


def filter_reply(text: str) -> tuple[str, dict]:
    """过滤她的回复：命中返回替换话术"""
    r = check(text)
    if r.get("hit"):
        return SAFE_REPLY, r
    return text, r


def reject_message(category: str = "") -> str:
    if category == "privacy":
        return "这个涉及别人的隐私，我不能帮你查或聊。"
    return "这个我不能聊，我们换个话题吧。"
