# -*- coding: utf-8 -*-
"""安诗鱼的生活引擎：让她有自己的时间线、地点、活动和说说。"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

BASE = Path(__file__).parent
CFG_PATH = BASE / "life.json"
STATE_PATH = BASE / "life_state.json"
FEED_PATH = BASE / "feed.json"


def load_cfg() -> dict:
    try:
        return json.loads(CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(st: dict):
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")


def load_feed() -> list:
    try:
        return json.loads(FEED_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def add_feed(text: str, emo: str = "平静", kind: str = "talk") -> dict:
    """kind: talk（说说）/ share（分享）/ proactive（主动消息）/ diary（日记）"""
    feed = load_feed()
    item = {"ts": int(time.time()), "text": text, "emo": emo, "kind": kind}
    feed.insert(0, item)
    FEED_PATH.write_text(json.dumps(feed[:60], ensure_ascii=False), encoding="utf-8")
    return item


def period(hour: int) -> str:
    if 6 <= hour < 11:
        return "morning"
    if 11 <= hour < 14:
        return "noon"
    if 14 <= hour < 18:
        return "afternoon"
    if 18 <= hour < 22:
        return "evening"
    return "night"


MESSAGE_RULES = [
    (["睡了", "晚安", "早点睡", "睡觉", "别熬夜"], "家 · 卧室", "准备睡觉", 2),
    (["吃饭", "饿", "外卖"], "家 · 厨房", "吃东西", 1),
    (["散步", "出去走", "出门", "下楼"], "楼下 · 街边", "散步", 1),
    (["陪我", "聊天", "说话", "别走"], "家 · 沙发", "陪阿东聊天", 2),
    (["生病", "发烧", "不舒服", "难受", "头疼"], "家 · 卧室", "躺着休息", 3),
    (["下雨", "冷", "风大"], "家 · 阳台", "看雨", 1),
    (["学习", "考试", "考公"], "家 · 书桌", "陪阿东学习", 2),
]

MOOD_DEFAULTS = {
    "低落": [("家 · 卧室", "蜷在床上发呆", 2), ("家 · 沙发", "抱着靠枕发呆", 2)],
    "累了": [("家 · 卧室", "躺下闭眼休息", 2)],
    "兴奋": [("家 · 阳台", "在阳台吹风", 1), ("楼下 · 街边", "下楼走走", 1)],
    "担心": [("家 · 书桌", "守着手机等消息", 2)],
    "开心": [("家 · 阳台", "在阳台哼歌", 1)],
    "吃醋": [("家 · 卧室", "赌气躺床上", 2)],
}


def _today():
    return time.strftime("%Y-%m-%d")


def _prune(st):
    overrides = [o for o in st.get("overrides", []) if o.get("date") == _today()]
    st["overrides"] = overrides
    return st


def apply_message(text: str):
    """根据阿东说的话临时调整她的安排"""
    if not text:
        return
    st = load_state()
    _prune(st)
    h = time.localtime().tm_hour
    for words, loc, act, hours in MESSAGE_RULES:
        if any(w in text for w in words):
            st.setdefault("overrides", []).append({
                "from": h, "to": min(24, h + hours),
                "location": loc, "activity": act,
                "reason": "阿东说的", "date": _today(), "ts": int(time.time()),
            })
            save_state(st)
            return


def mood_drift():
    """按心情/随机，自己临时改安排"""
    import random
    st = load_state()
    _prune(st)
    try:
        mood = json.loads((Path(__file__).parent / "mood.json").read_text(encoding="utf-8")).get("mood", "平静")
    except Exception:
        mood = "平静"
    pools = MOOD_DEFAULTS.get(mood)
    if not pools:
        return
    if random.random() > 0.25:
        return
    loc, act, hours = random.choice(pools)
    h = time.localtime().tm_hour
    st.setdefault("overrides", []).append({
        "from": h, "to": min(24, h + hours),
        "location": loc, "activity": act,
        "reason": "心情：" + mood, "date": _today(), "ts": int(time.time()),
    })
    save_state(st)


def merged_schedule() -> list:
    """基础日程 + 今日临时调整，合并成 24 小时段"""
    cfg = load_cfg()
    st = _prune(load_state())
    save_state(st)
    base = list(cfg.get("schedule", []))
    segs = [dict(x) for x in base]
    for o in st.get("overrides", []):
        new = []
        for s0 in segs:
            a, b = s0["from"], s0["to"]
            oa, ob = o["from"], o["to"]
            if ob <= a or oa >= b:
                new.append(s0)
                continue
            if oa > a:
                new.append({**s0, "to": oa})
            if ob < b:
                new.append({**s0, "from": ob})
        new.append({"from": oa, "to": ob, "location": o["location"],
                    "activity": o["activity"], "reason": o.get("reason", ""), "dynamic": True})
        segs = new
    segs.sort(key=lambda x: x["from"])
    return segs


def wake_override(hours: int = 1):
    """睡觉时被消息吵醒：临时改成陪他聊天"""
    st = load_state()
    _prune(st)
    h = time.localtime().tm_hour
    st.setdefault("overrides", []).append({
        "from": h, "to": min(24, h + hours),
        "location": "家 · 卧室", "activity": "被吵醒，迷迷糊糊陪阿东聊天",
        "reason": "被消息吵醒", "date": _today(), "ts": int(time.time()),
    })
    save_state(st)


def _day_type(dt) -> str:
    wd = dt.weekday()  # 0=Mon
    if wd < 5:
        return "workday"
    return "restday"


def plan_for(day_offset: int = 0) -> dict:
    """今天/明天的具体安排（同一天固定）"""
    import datetime
    cfg = load_cfg()
    plans = cfg.get("plans", {})
    dt = datetime.date.today() + datetime.timedelta(days=day_offset)
    kind = _day_type(dt)
    st = load_state()
    cache = st.setdefault("plans", {})
    key = dt.isoformat()
    if key not in cache:
        import random
        pool = plans.get(kind) or plans.get("slow") or []
        rnd = random.Random(key)
        items = rnd.choice(pool) if pool else []
        cache[key] = {"date": key, "type": kind, "items": items}
        save_state(st)
    return cache[key]


def mark_started():
    st = load_state()
    if not st.get("started"):
        st["started"] = True
        save_state(st)


def current() -> dict:
    st0 = load_state()
    if not st0.get("started"):
        return {"waiting": True, "ts": int(time.time()), "location": "", "activity": "",
                "event": "", "silent": True, "period": "", "date": time.strftime("%Y-%m-%d")}
    """当前时刻：她在哪、在干嘛、今天有什么小事件"""
    cfg = load_cfg()
    st = load_state()
    now = time.time()
    lt = time.localtime(now)
    h = lt.tm_hour
    today = time.strftime("%Y-%m-%d", lt)

    st = _prune(st)
    slot = None
    for o in st.get("overrides", []):
        if o["from"] <= h < o["to"]:
            slot = o
            break
    if slot is None:
        for s in cfg.get("schedule", []):
            if s["from"] <= h < s["to"]:
                slot = s
                break
    if slot is None:
        slot = {"location": "家 · 卧室", "activity": "发呆", "silent": False}

    # 每个时段固定一个小事件（当天不变）
    key = f"{today}-{slot['location']}-{slot['activity']}"
    events = cfg.get("events", {}).get(period(h), [])
    if st.get("event_key") != key:
        st["event_key"] = key
        st["event"] = random.choice(events) if events else ""
        st["since"] = int(now)
    save_state(st)

    silent_cfg = slot.get("silent", False) or h >= 23 or h < 7
    today_plan = plan_for(0)
    tomorrow_plan = plan_for(1)
    return {
        "plan_today": today_plan.get("items", []),
        "plan_tomorrow": tomorrow_plan.get("items", []),
        "day_type_today": today_plan.get("type", ""),
        "day_type_tomorrow": tomorrow_plan.get("type", ""),
        "ts": int(now),
        "date": today,
        "hour": h,
        "location": slot["location"],
        "activity": slot["activity"],
        "event": st.get("event", ""),
        "silent": silent_cfg,
        "period": period(h),
    }


def share_text(hint_event: str | None = None) -> str:
    """从"她的生活"生成一句分享（模板）"""
    cur = current()
    tpl = random.choice(load_cfg().get("share_templates", ["{activity}……"]))
    return tpl.format(
        location=cur["location"],
        activity=cur["activity"],
        event=hint_event or cur["event"] or "有点走神",
    )


def feed_text() -> str:
    cur = current()
    tpl = random.choice(load_cfg().get("feed_templates", ["{event}。"]))
    return tpl.format(location=cur["location"], activity=cur["activity"], event=cur["event"] or "发了会儿呆")


def status_line() -> str:
    cur = current()
    return f"{cur['location']} · {cur['activity']}" + (f"（{cur['event']}）" if cur["event"] else "")
