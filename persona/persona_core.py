# -*- coding: utf-8 -*-
"""安诗鱼人格核心（纯逻辑，不依赖 AstrBot，便于测试）。

职责：
1. 由 persona.json 生成系统提示词
2. 心情状态机（随对话变化、随时间衰减）
3. 称呼 / 亲密度 / 时间感知
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

BASE = Path(__file__).parent
CFG_PATH = BASE / "persona.json"
MOOD_PATH = BASE / "mood.json"

MOOD_RULES = [
    ("担心", ["生病", "发烧", "头疼", "难受", "受伤", "疼", "失眠", "过敏", "医院"]),
    ("低落", ["难过", "想哭", "哭了", "烦", "累", "压力", "孤独", "没意思", "想放弃"]),
    ("吃醋", ["别人", "女生", "男生", "朋友", "同学", "喜欢她", "喜欢他"]),
    ("着急", ["在吗", "回我", "怎么不回", "快点", "急", "等你", "人呢"]),
    ("烦", ["烦", "别烦", "吵", "闭嘴", "你好烦", "无聊"]),
    ("开心", ["喜欢", "开心", "哈哈", "好耶", "太好了", "想你", "爱你", "夸"]),
    ("兴奋", ["计划", "去玩", "电影", "游戏", "买", "冲", "期待"]),
]


def owner_name() -> str:
    """他告诉过我的名字；不知道就返回空串"""
    try:
        d = json.loads((Path(__file__).parent / "owner.json").read_text(encoding="utf-8"))
        return (d.get("name") or "").strip()
    except Exception:
        return ""


def set_owner_name(name: str):
    if not name:
        return
    (Path(__file__).parent / "owner.json").write_text(
        json.dumps({"name": name.strip()}, ensure_ascii=False), encoding="utf-8")


def load_config() -> dict:
    try:
        return json.loads(CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_mood() -> dict:
    try:
        return json.loads(MOOD_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"mood": "平静", "score": 0.5, "ts": int(time.time()), "turns": 0}


def _save_mood(m: dict):
    try:
        MOOD_PATH.write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def current_mood() -> dict:
    m = _load_mood()
    # 半衰期衰减，慢慢回到平静
    cfg = load_config().get("mood", {})
    half = max(10, int(cfg.get("half_life_minutes", 90))) * 60
    age = max(0, int(time.time()) - int(m.get("ts", 0)))
    if age > 0:
        decay = 0.5 ** (age / half)
        m["score"] = 0.5 + (float(m.get("score", 0.5)) - 0.5) * decay
        m["ts"] = int(time.time())
        if abs(m["score"] - 0.5) < 0.08:
            m["mood"] = "平静"
        _save_mood(m)
    return m


def update_mood(text: str) -> dict:
    """根据阿东这句话更新心情"""
    m = _load_mood()
    text = text or ""
    mood = m.get("mood", "平静")
    score = float(m.get("score", 0.5))
    for label, words in MOOD_RULES:
        if any(w in text for w in words):
            mood = label
            if label in ("开心", "兴奋"):
                score = min(1.0, score + 0.18)
            else:
                score = max(0.0, score - 0.15)
            break
    m.update({"mood": mood, "score": round(score, 3), "ts": int(time.time()),
              "turns": int(m.get("turns", 0)) + 1})
    _save_mood(m)
    return m


def intimacy_level(turns: int) -> str:
    levels = load_config().get("relationship", {}).get("intimacy_levels", [])
    if not levels:
        return ""
    if turns < 30:
        return levels[0]
    if turns < 200:
        return levels[1]
    if turns < 800:
        return levels[2]
    return levels[-1]


def time_phrase(ts: float | None = None) -> str:
    h = time.localtime(ts).tm_hour
    if h < 5:
        return "凌晨"
    if h < 8:
        return "清晨"
    if h < 11:
        return "早上"
    if h < 14:
        return "中午"
    if h < 18:
        return "下午"
    if h < 23:
        return "晚上"
    return "深夜"


def build_system_prompt(memories: list[str] | None = None, last_reply: str = "", life: dict | None = None) -> str:
    cfg = load_config()
    m = current_mood()
    name = cfg.get("name", "安诗鱼")
    owner = owner_name() or cfg.get("owner_name", "").strip()
    tr = cfg.get("traits", {})
    sp = cfg.get("speech", {})

    level = intimacy_level(int(m.get("turns", 0)))
    catch = "、".join(sp.get("catchphrases", [])[:4])
    banned = "；".join(sp.get("forbidden", []))
    rules = "\n".join(f"- {r}" for r in cfg.get("rules", []))

    lines = [
        (f"你是「{name}」，{cfg.get('species', '')}。你的称呼是「{name}」。"
         + (f"你称呼他「{owner}」。" if owner else "你还不知道他的名字，暂时直接对他说「你」，不要乱编称呼。")),
        f"【来历】{cfg.get('story', '')}",
        f"【性格】黏人 {tr.get('clingy', 0.8)}、爱闹 {tr.get('teasing', 0.5)}、"
        f"护短 {tr.get('protective', 0.8)}、好奇 {tr.get('curious', 0.6)}、"
        f"小脾气 {tr.get('grumpy', 0.3)}（按这些比例表现，不要全用满）",
        f"【说话】像真人发消息：短句口语，一次最多 {sp.get('max_sentences', 3)} 句；"
        f"不用客服腔，不用括号写动作；偶尔用口头禅（{catch}）；"
        f"禁用这些话：{banned}",
        f"【此刻】时间：{time_phrase()}；心情：{m.get('mood', '平静')}；"
        f"你和{owner or '他'}的关系：{level}",
    ]
    if life:
        loc = life.get("location") or ""
        act = life.get("activity") or ""
        if life.get("silent"):
            lines.append("【你此刻的状态】现在是你的睡觉时间，你已经睡了，被这条消息吵醒。"
                         "你说话会慢半拍、带着困意、有点小脾气（但不会真的生气），回复要短。")
        elif act:
            lines.append(f"【你此刻的状态】你正在{loc}做「{act}」" + (f"（刚发生：{life.get('event')}）" if life.get("event") else "") +
                         "。回复要带一点这个场景的痕迹，不要像专门守着手机聊天。")
            if "被吵醒" in act:
                lines.append("你刚被吵醒，还困着：说话短、迷糊、带困意，别太精神。")
        if loc or act:
            lines.append("如果阿东问你此刻在干嘛/在做什么，就按上面此刻的状态如实回答，不要答得像在守着他聊天。")
        if life.get("plan_today"):
            lines.append("【你今天的安排】" + "；".join(life["plan_today"]))
        if life.get("plan_tomorrow"):
            lines.append("【你明天的安排】" + "；".join(life["plan_tomorrow"]))
        if life.get("plan_today") or life.get("plan_tomorrow"):
            lines.append("如果阿东问起你明天/今天有没有空、有没有事，就按上面的安排自然地回答；"
                         "没写在安排里的事，就说不确定/还没想好，别编。")
    if last_reply:
        lines.append(f"【上一条你说过】{last_reply[:60]}（不要重复同样的说法）")
    if memories:
        lines.append("【你记得的事】\n" + "\n".join(f"- {x}" for x in memories[:4]))
    lines.append("【规矩】" + ("\n" + rules if rules else ""))
    return "\n\n".join(lines)
