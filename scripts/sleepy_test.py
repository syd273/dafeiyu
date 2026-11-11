import sys, requests
from pathlib import Path
sys.path.insert(0, r"D:\大肥鱼\persona")
import persona_core, life_core
life_core._prune(life_core.load_state())
lifedata = {"location": "家 · 卧室", "activity": "睡觉", "event": "", "silent": True}
KEY = Path(r"D:\大肥鱼\deepseek-key.txt").read_text(encoding="utf-8").strip()
sysp = persona_core.build_system_prompt(life=lifedata)
for msg in ["在吗", "你怎么不理我"]:
    body = {"model":"deepseek-chat","messages":[{"role":"system","content":sysp},{"role":"user","content":msg}],"temperature":0.9,"max_tokens":150}
    s = requests.Session(); s.trust_env=False
    r = s.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json=body, timeout=60)
    print("你：", msg)
    print("安诗鱼：", r.json()["choices"][0]["message"]["content"].strip(), "\n")