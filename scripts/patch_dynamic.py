from pathlib import Path
import ast

p = Path(r"D:\大肥鱼\persona\life_core.py")
s = p.read_text(encoding="utf-8")

# 1) 加入动态覆盖机制
if "def apply_message" not in s:
    s = s.replace("def mark_started():", '''MESSAGE_RULES = [
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


def mark_started():''')

    # current() 优先使用 override
    s = s.replace('''    slot = None
    for s in cfg.get("schedule", []):
        if s["from"] <= h < s["to"]:
            slot = s
            break''', '''    st = _prune(st)
    slot = None
    for o in st.get("overrides", []):
        if o["from"] <= h < o["to"]:
            slot = o
            break
    if slot is None:
        for s in cfg.get("schedule", []):
            if s["from"] <= h < s["to"]:
                slot = s
                break''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("life dynamic ok")

# 2) sync：应用阿东的话 + 心情漂移 + 输出合并日程
p = Path(r"D:\大肥鱼\scripts\sync_memories.py")
s = p.read_text(encoding="utf-8")
if "mood_drift" not in s:
    s = s.replace('    try:\n        import json as _json\n        life = _json.loads((src_dir / "life.json").read_text(encoding="utf-8"))',
'''    try:
        import json as _json
        import sqlite3 as _sq2
        cc = _sq2.connect(BASE / "memory" / "archive.db")
        last_user = cc.execute("SELECT text FROM messages WHERE role='user' ORDER BY id DESC LIMIT 1").fetchone()
        cc.close()
        if last_user and last_user[0] and life_core is not None:
            life_core.apply_message(last_user[0])
            life_core.mood_drift()
    except Exception:
        pass
    try:
        import json as _json
        life = _json.loads((src_dir / "life.json").read_text(encoding="utf-8"))''')
    s = s.replace('(dst_dir / "schedule.json").write_text(_json.dumps(\n            {"schedule": life.get("schedule", [])}, ensure_ascii=False), encoding="utf-8")',
                  '(dst_dir / "schedule.json").write_text(_json.dumps(\n            {"schedule": (life_core.merged_schedule() if life_core is not None else life.get("schedule", []))}, ensure_ascii=False), encoding="utf-8")')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("sync dynamic ok")