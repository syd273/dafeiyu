from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_soul\main.py")
s = p.read_text(encoding="utf-8")
s = s.replace("""            if life is not None:
                life_state = life.current()""",
"""            if life is not None:
                life_state = life.current()
                if life_state.get("waiting"):
                    life.mark_started()
                    life_state = life.current()""")
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("first-message start ok")