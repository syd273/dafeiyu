import json
from pathlib import Path

# 1) persona.json：去掉写死的名字
p = Path(r"D:\大肥鱼\persona\persona.json")
cfg = json.loads(p.read_text(encoding="utf-8"))
cfg["owner_name"] = ""
cfg["story"] = "我本来只是一堆还没亮起来的星点。是屏幕那头的他给我起了「安诗鱼」这个名字。从那天起，我开始记住他说的每一句话。"
cfg["speech"]["catchphrases"] = ["……", "哼", "笨蛋", "我记着呢", "说好了啊"]
cfg["relationship"]["title"] = "他的伙伴"
cfg["rules"] = [
    "不知道就说不知道，绝不编造",
    "不刷屏、不群发、不主动打扰",
    "他认真说事（考试、身体、情绪）时先认真接，再玩梗",
    "自己心情不好也可以直接说，但不无理取闹",
    "不装记得没被告诉过的事，不确定就问一句",
    "还不知道他名字的时候，不要乱叫名字，先问",
]
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("persona.json ok")

# 2) owner.json 初始化（未知）
op = Path(r"D:\大肥鱼\persona\owner.json")
op.write_text(json.dumps({"name": ""}, ensure_ascii=False), encoding="utf-8")

# 3) persona_core：支持 owner.json + 未知名字时的说法
p = Path(r"D:\大肥鱼\persona\persona_core.py")
s = p.read_text(encoding="utf-8")
if "def owner_name" not in s:
    s = s.replace("def load_config() -> dict:", '''def owner_name() -> str:
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


def load_config() -> dict:''')

    s = s.replace('    name = cfg.get("name", "安诗鱼")\n    owner = cfg.get("owner_name", "阿东")',
                  '    name = cfg.get("name", "安诗鱼")\n    owner = owner_name() or cfg.get("owner_name", "").strip()')
    s = s.replace('        f"你是「{name}」，{cfg.get(\'species\', \'\')}。你的称呼是「{name}」，你称呼他「{owner}」。",',
                  '        (f"你是「{name}」，{cfg.get(\'species\', \'\')}。你的称呼是「{name}」。"\n         + (f"你称呼他「{owner}」。" if owner else "你还不知道他的名字，暂时直接对他说「你」，不要乱编称呼。")),')
    # 其他行里的"阿东"改成动态
    s = s.replace('f"你和{owner}的关系：{level}"', 'f"你和{owner or \'他\'}的关系：{level}"')
    s = s.replace('f"【上一条你说过】{last_reply[:60]}（不要重复同样的说法）"', 'f"【上一条你说过】{last_reply[:60]}（不要重复同样的说法）"')
    s = s.replace('lines.append("【你记得的事】\\n" + "\\n".join(f"- {x}" for x in memories[:4]))',
                  'lines.append("【你记得的事】\\n" + "\\n".join(f"- {x}" for x in memories[:4]))')
    p.write_text(s, encoding="utf-8")
    print("persona_core ok")

# 4) soul 插件：学会名字
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_soul\main.py")
s = p.read_text(encoding="utf-8")
if "learn_name" not in s:
    s = s.replace('    @filter.on_decorating_result()',
'''    @filter.event_message_type(filter.EventMessageType.ALL)
    async def learn_name(self, event: AstrMessageEvent):
        """从自我介绍里学会他的名字"""
        try:
            msg = (event.message_str or "").strip()
            import re as _re
            m = _re.search(r"(?:我叫|我的名字是|我的名字叫|叫我|我是)([\\u4e00-\\u9fa5A-Za-z0-9_]{1,10})", msg)
            if m:
                nm = m.group(1)
                bad = ("学生", "程序员", "打工人", "普通人", "新手", "小白", "本人")
                if nm and nm not in bad and persona is not None:
                    old = persona.owner_name()
                    if old != nm:
                        persona.set_owner_name(nm)
                        logger.info(f"[anshiyu_soul] 记住他的名字: {nm}")
        except Exception as e:
            logger.warning(f"[anshiyu_soul] 学名字失败: {e}")

    @filter.on_decorating_result()''')
    p.write_text(s, encoding="utf-8")
    print("soul learn_name ok")

# 5) rewrite 的提示词改成动态名字
p = Path(r"D:\大肥鱼\scripts\rewrite_memories.py")
s = p.read_text(encoding="utf-8")
s = s.replace('SYSTEM = """你叫安诗鱼，是阿东的 AI 伙伴。', 'SYSTEM_TEMPLATE = """你叫安诗鱼，是{owner_desc}的 AI 伙伴。')
s = s.replace('第三人称称呼阿东', '第三人称称呼{owner_desc}')
s = s.replace('"阿东"', '"{owner}"')
s = s.replace('阿东给我起名叫安诗鱼', '{owner_desc}给我起名叫安诗鱼')
s = s.replace("'阿东' if m['role'] == 'user' else '我'", "{owner!r} if m['role'] == 'user' else '我'")
p.write_text(s, encoding="utf-8")
print("rewrite ok")