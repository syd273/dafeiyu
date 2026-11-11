from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
if "_PROACTIVE_FREQ" not in s:
    s = s.replace("async def proactive_loop():",
'''_PROACTIVE_FREQ = {
    "low": {"max_per_day": 2, "min_gap_minutes": 240},
    "medium": {"max_per_day": 4, "min_gap_minutes": 120},
    "high": {"max_per_day": 6, "min_gap_minutes": 60},
}


async def proactive_loop():''')
    # 在读取 cfg 后应用频率
    s = s.replace('''            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))''',
'''            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            try:
                freq = _PROACTIVE_FREQ.get(_personality().get("proactive", "medium"), {})
                for k, v in freq.items():
                    cfg[k] = v
            except Exception:
                pass''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("主动频率已关联")