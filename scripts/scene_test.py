import sys, requests
from pathlib import Path
sys.path.insert(0, r"D:\大肥鱼\persona")
import persona_core
KEY = Path(r"D:\大肥鱼\deepseek-key.txt").read_text(encoding="utf-8").strip()
cases = [
    ("白天正在书桌忙", {"location": "家 · 书桌", "activity": "忙手上的事", "event": "写东西写到一半卡住了", "silent": False}, "在吗，快点回我"),
    ("晚上阳台放松", {"location": "家 · 阳台", "activity": "放松，看外面", "event": "阳台风很大，但很舒服", "silent": False}, "我今天好累"),
    ("睡前躺着刷手机", {"location": "家 · 卧室", "activity": "躺着刷手机", "event": "刷到好笑的东西", "silent": False}, "晚安啦"),
]
s = requests.Session(); s.trust_env = False
for tag, life, msg in cases:
    persona_core.update_mood(msg)
    sysp = persona_core.build_system_prompt(life=life)
    body = {"model":"deepseek-chat","messages":[{"role":"system","content":sysp},{"role":"user","content":msg}],"temperature":0.9,"max_tokens":160}
    r = s.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json=body, timeout=60)
    print(f"[{tag}] 心情={persona_core.current_mood().get('mood')}")
    print("你：", msg)
    print("安诗鱼：", r.json()["choices"][0]["message"]["content"].strip(), "\n")