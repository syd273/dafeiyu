from pathlib import Path
import json
p = Path(r"D:\大肥鱼\persona\proactive.json")
cfg = json.loads(p.read_text(encoding="utf-8"))
ids = [x["id"] for x in cfg["types"]]
if "bili" not in ids:
    cfg["types"].append({"id": "bili", "window": [11, 23], "weight": 1.1,
                         "hint": "你刚在B站刷到一个视频，想分享给阿东看看"})
cfg.setdefault("token_low_threshold", 5.0)
cfg.setdefault("token_check_minutes", 60)
cfg.setdefault("token_alert_hours", 12)
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("config ok, types:", [x["id"] for x in cfg["types"]])