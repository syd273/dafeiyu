import json
from pathlib import Path

# 1) life.json 增加日程计划模板
p = Path(r"D:\大肥鱼\persona\life.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["plans"] = {
    "workday": [
        ["上午在书桌前做事", "下午继续手上的活", "晚上早点休息"],
        ["上午整理资料、写东西", "下午出去买点东西", "晚上看看剧"],
        ["上午处理杂事", "下午把没做完的事收尾", "晚上发呆/早点睡"],
    ],
    "restday": [
        ["睡到自然醒", "下午收拾房间、洗衣服", "晚上追剧或看综艺"],
        ["上午赖床", "下午出门走走、逛逛", "晚上很早就困了"],
        ["今天没安排，在家发呆", "下午煮点好吃的", "晚上在阳台看星星"],
    ],
    "slow": [
        ["上午慢慢来", "下午做了件小事", "晚上很早就困了"],
        ["今天状态一般，只想安静待着", "下午躺了一会儿", "晚上早早躺下"],
    ],
}
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("life.json plans ok")

# 2) life_core 生成今天/明天的计划
p = Path(r"D:\大肥鱼\persona\life_core.py")
s = p.read_text(encoding="utf-8")
if "def plan_for" not in s:
    s = s.replace("def mark_started():", '''def _day_type(dt) -> str:
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


def mark_started():''')
    # current() 带上今天/明天安排
    s = s.replace('''    silent_cfg = slot.get("silent", False) or h >= 23 or h < 7
    return {
        "ts": int(now),''', '''    silent_cfg = slot.get("silent", False) or h >= 23 or h < 7
    today_plan = plan_for(0)
    tomorrow_plan = plan_for(1)
    return {
        "plan_today": today_plan.get("items", []),
        "plan_tomorrow": tomorrow_plan.get("items", []),
        "day_type_today": today_plan.get("type", ""),
        "day_type_tomorrow": tomorrow_plan.get("type", ""),
        "ts": int(now),''')
    p.write_text(s, encoding="utf-8")
    print("life_core plan ok")

# 3) persona_core：把安排写进提示词
p = Path(r"D:\大肥鱼\persona\persona_core.py")
s = p.read_text(encoding="utf-8")
if "plan_tomorrow" not in s:
    s = s.replace('''            if "被吵醒" in act:''', '''            if life.get("plan_today"):
                lines.append("【你今天的安排】" + "；".join(life["plan_today"]))
            if life.get("plan_tomorrow"):
                lines.append("【你明天的安排】" + "；".join(life["plan_tomorrow"]))
            if "被吵醒" in act:''')
    p.write_text(s, encoding="utf-8")
    print("persona plan ok")