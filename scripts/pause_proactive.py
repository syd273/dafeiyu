import json
from pathlib import Path
p = Path(r"D:\大肥鱼\persona\proactive.json")
cfg = json.loads(p.read_text(encoding="utf-8"))
cfg["enabled"] = True
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("proactive enabled")