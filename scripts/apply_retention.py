from pathlib import Path
import ast

# 1) sync_memories：导出时附加 retention
p = Path(r"D:\大肥鱼\scripts\sync_memories.py")
s = p.read_text(encoding="utf-8")
if "retention" not in s:
    s = s.replace(
        'STATE = Path(r"D:\\大肥鱼\\memory\\.sync_state.json")',
        'STATE = Path(r"D:\\大肥鱼\\memory\\.sync_state.json")\nPERSONA_DIR = Path(r"D:\\大肥鱼\\persona")'
    )
    s = s.replace(
        "def save_out(items: list):",
        "def save_out(items: list):\n    try:\n        import sys\n        if str(PERSONA_DIR) not in sys.path:\n            sys.path.insert(0, str(PERSONA_DIR))\n        import retention\n        items = retention.annotate(items)\n    except Exception as e:\n        print('[sync] retention 失败:', e, flush=True)"
    )
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("sync patched")

# 2) 星图前端：亮度/大小随保持度
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
old = """    const c = starColor('arm');
    col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
    size[i] = 0.32 + Math.pow(Math.random(), 3) * 0.85;"""
new = """    const c = starColor('arm');
    const ret = (typeof m.retention === 'number') ? m.retention : 0.6;   // 艾宾浩斯保持度
    const dim = 0.45 + 0.55 * ret;
    col[i * 3] = c[0] * dim; col[i * 3 + 1] = c[1] * dim; col[i * 3 + 2] = c[2] * dim;
    size[i] = (0.32 + Math.pow(Math.random(), 3) * 0.85) * (0.55 + 0.75 * ret);"""
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("starmap patched")
else:
    print("starmap MISS")

# 3) 主动插件：remember 类型（主动想起快忘的事）
p = Path(r"D:\大肥鱼\persona\proactive.json")
import json
cfg = json.loads(p.read_text(encoding="utf-8"))
ids = [x["id"] for x in cfg["types"]]
if "remember" not in ids:
    cfg["types"].append({
        "id": "remember", "window": [10, 22], "weight": 0.8,
        "hint": "你突然想起一件很久没想起的事（关于阿东），想跟他说",
        "need_silence_hours": 3,
    })
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("proactive remember type ok")