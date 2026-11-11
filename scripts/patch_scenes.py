from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 1) 插入场景过滤辅助函数（在 proactive_loop 之前）
anchor = "async def proactive_loop():"
helper = '''def _last_user_ts() -> int:
    try:
        conn = kernel.connect()
        try:
            row = conn.execute("SELECT MAX(ts) FROM messages WHERE role='user'").fetchone()
            return int(row[0] or 0)
        finally:
            conn.close()
    except Exception:
        return 0


def _recent_text(hours: int = 48, limit: int = 40) -> str:
    try:
        conn = kernel.connect()
        try:
            rows = conn.execute(
                "SELECT text FROM messages WHERE ts>=? ORDER BY id DESC LIMIT ?",
                (int(time.time()) - hours * 3600, limit),
            ).fetchall()
            return "\\n".join(r["text"] for r in rows if r["text"])
        finally:
            conn.close()
    except Exception:
        return ""


def _pick_scene(types, h, now, mood_label, last_user_ts):
    """按窗口/星期/心情/沉默时长/关键词过滤，再按权重随机选择"""
    import random as _random
    wd = time.localtime(now).tm_wday  # 0=周一
    is_weekend = wd >= 5
    text_now = _recent_text()
    cands = []
    for t in types:
        w0, w1 = t.get("window", [0, 24])
        if not (w0 <= h < w1):
            continue
        days = t.get("days")
        if days == "weekday" and is_weekend:
            continue
        if days == "weekend" and not is_weekend:
            continue
        mood_cond = t.get("mood")
        if mood_cond and mood_label not in mood_cond:
            continue
        silence_h = t.get("need_silence_hours")
        if silence_h and now - last_user_ts < silence_h * 3600:
            continue
        kws = t.get("need_keywords")
        if kws and not any(k in text_now for k in kws):
            continue
        cands.append(t)
    if not cands:
        return None
    weights = [float(t.get("weight", 1.0)) for t in cands]
    return _random.choices(cands, weights=weights, k=1)[0]


async def proactive_loop():'''
if "_pick_scene" not in s:
    s = s.replace(anchor, helper)
    print("helper added")

# 2) 替换类型选择逻辑
old = '''            # 挑一个类型
            types = [t for t in cfg.get("types", []) if t["window"][0] <= h < t["window"][1]]
            if not types:
                continue
            pick = types[int(now) % len(types)]'''
new = '''            # 挑一个类型（窗口/星期/心情/沉默/关键词 + 权重随机）
            try:
                mood_label = persona_core.current_mood().get("mood", "平静")
            except Exception:
                mood_label = "平静"
            pick = _pick_scene(cfg.get("types", []), h, now, mood_label, _last_user_ts())
            if not pick:
                continue'''
if old in s:
    s = s.replace(old, new)
    print("scene picking replaced")

# 3) 新增主动场景测试接口
if "/api/proactive/test" not in s:
    s = s.replace('@app.post("/api/share/auto")', '''@app.post("/api/proactive/test")
async def proactive_test(token: str = Query(""), type_id: str = Query("")):
    """测试某个主动场景的文案（不广播、不写库）"""
    auth(token)
    cfg = json.loads((BASE / "persona" / "proactive.json").read_text(encoding="utf-8"))
    types = cfg.get("types", [])
    if type_id:
        pick = next((t for t in types if t.get("id") == type_id), None)
    else:
        pick = _pick_scene(types, time.localtime().tm_hour, time.time(),
                           persona_core.current_mood().get("mood", "平静"), _last_user_ts())
    if not pick:
        return {"ok": False, "error": "no matching scene"}
    life = life_core.current()
    system = persona_core.build_system_prompt(life=life)
    hint = pick.get("hint", "随便跟他说句话")
    if pick.get("id") == "life":
        hint = f"你此刻在{life.get('location')}，正在{life.get('activity')}。想跟他说句话。"
    system += f"\\n\\n现在你要主动给他发一条消息。{hint}\\n要求：只输出消息本身，1-2句，口语，不要解释。"
    text = ask_llm(system, [{"role": "user", "content": "（主动发一条）"}], max_tokens=200)
    return {"ok": bool(text), "scene": pick.get("id"), "text": text or ""}


@app.post("/api/share/auto")''')
    print("proactive test route added")

p.write_text(s, encoding="utf-8")
ast.parse(s)
print("app.py patched")