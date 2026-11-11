import sys, requests
from pathlib import Path
sys.path.insert(0, r"D:\大肥鱼\persona")
import persona_core, life_core
life_core.mark_started()
cur = life_core.current()
print("此刻:", cur.get("location"), cur.get("activity"))
print("今天安排:", cur.get("plan_today"))
print("明天安排:", cur.get("plan_tomorrow"))
KEY = Path(r"D:\大肥鱼\deepseek-key.txt").read_text(encoding="utf-8").strip()
sysp = persona_core.build_system_prompt(life=cur)
s = requests.Session(); s.trust_env = False
for msg in ["你明天有没有工作啊", "那你现在在干嘛"]:
    body = {"model":"deepseek-chat","messages":[{"role":"system","content":sysp},{"role":"user","content":msg}],"temperature":0.9,"max_tokens":180}
    r = s.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json=body, timeout=60)
    print("你：", msg)
    print("安诗鱼：", r.json()["choices"][0]["message"]["content"].strip(), "\n")