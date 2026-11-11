from pathlib import Path
import ast

# 1) persona_core：更多心情触发 + 生活状态注入
p = Path(r"D:\大肥鱼\persona\persona_core.py")
s = p.read_text(encoding="utf-8")
if "you_are_asleep" not in s:
    s = s.replace('    ("开心", ["喜欢", "开心", "哈哈", "好耶", "太好了", "想你", "爱你", "夸"]),',
'''    ("着急", ["在吗", "回我", "怎么不回", "快点", "急", "等你", "人呢"]),
    ("烦", ["烦", "别烦", "吵", "闭嘴", "你好烦", "无聊"]),
    ("开心", ["喜欢", "开心", "哈哈", "好耶", "太好了", "想你", "爱你", "夸"]),''')
    s = s.replace('def build_system_prompt(memories: list[str] | None = None, last_reply: str = "") -> str:',
                  'def build_system_prompt(memories: list[str] | None = None, last_reply: str = "", life: dict | None = None) -> str:')
    s = s.replace('''    if last_reply:
        lines.append(f"【上一条你说过】{last_reply[:60]}（不要重复同样的说法）")''',
'''    if life:
        loc = life.get("location") or ""
        act = life.get("activity") or ""
        if life.get("silent"):
            lines.append("【你此刻的状态】现在是你的睡觉时间，你已经睡了，被这条消息吵醒。"
                         "你说话会慢半拍、带着困意、有点小脾气（但不会真的生气），回复要短。")
        elif act:
            lines.append(f"【你此刻的状态】你正在{loc}做「{act}」" + (f"（刚发生：{life.get('event')}）" if life.get("event") else "") +
                         "。回复要带一点这个场景的痕迹，不要像专门守着手机聊天。")
    if last_reply:
        lines.append(f"【上一条你说过】{last_reply[:60]}（不要重复同样的说法）")''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("persona life-aware ok")

# 2) life_core：被吵醒后临时陪聊
p = Path(r"D:\大肥鱼\persona\life_core.py")
s = p.read_text(encoding="utf-8")
if "def wake_override" not in s:
    s = s.replace("def mark_started():", '''def wake_override(hours: int = 1):
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


def mark_started():''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("life wake override ok")

# 3) soul 插件：把生活状态注入提示词，睡觉被吵醒则改日程
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_soul\main.py")
s = p.read_text(encoding="utf-8")
if "life_core" not in s:
    s = s.replace('''persona = None
for p_dir in PERSONA_DIRS:''', '''persona = None
life = None
for p_dir in PERSONA_DIRS:''')
    s = s.replace('''        try:
            import persona_core as _pc  # type: ignore

            persona = _pc''', '''        try:
            import persona_core as _pc  # type: ignore
            import life_core as _lc  # type: ignore

            persona = _pc
            life = _lc''')
    s = s.replace('''        # 把记忆插件已经注入的内容原样保留，这里只加人格
        prompt = persona.build_system_prompt(memories=None, last_reply=self.last_reply)''',
'''        # 她此刻的状态
        life_state = None
        try:
            if life is not None:
                life_state = life.current()
                if life_state.get("silent"):
                    life.wake_override()
                    life_state = life.current()
        except Exception:
            life_state = None
        # 把记忆插件已经注入的内容原样保留，这里只加人格
        prompt = persona.build_system_prompt(memories=None, last_reply=self.last_reply, life=life_state)''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("soul life-aware ok")