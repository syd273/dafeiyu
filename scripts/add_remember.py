from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_proactive\main.py")
s = p.read_text(encoding="utf-8")

if "remember_memory" not in s:
    s = s.replace(
"""try:
    import life_core
except Exception:
    life_core = None""",
"""try:
    import life_core
except Exception:
    life_core = None
try:
    import retention as retention_mod
except Exception:
    retention_mod = None""")

    s = s.replace(
'        if pick["id"] == "life" and life_core is not None:',
'''        remember_memory = ""
        if pick["id"] == "remember":
            try:
                import json as _json
                stars = _json.loads(Path(r"D:\\大肥鱼\\milky-way-3d\\memory_stars.json").read_text(encoding="utf-8"))
                cands = [x for x in stars
                         if isinstance(x.get("retention"), (int, float))
                         and x["retention"] < 0.45
                         and time.time() - int(x.get("ts", 0)) > 2 * 86400]
                if cands:
                    cands.sort(key=lambda x: x["retention"])
                    remember_memory = cands[0].get("view") or cands[0].get("text", "")
            except Exception:
                remember_memory = ""
            if not remember_memory:
                return
            hint = f"你突然想起这件事：{remember_memory}。想跟他说一句，自然点，别像复述。"
        if pick["id"] == "life" and life_core is not None:''')

    s = s.replace(
"            st[\"sent_texts\"] = (st.get(\"sent_texts\", []) + [text])[-20:]",
"            st[\"sent_texts\"] = (st.get(\"sent_texts\", []) + [text])[-20:]\n            if remember_memory and retention_mod is not None:\n                try:\n                    retention_mod.review(remember_memory)\n                    logger.info(\"[anshiyu_proactive] 复习了一条旧记忆\")\n                except Exception:\n                    pass")
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("remember type added")
else:
    print("already")