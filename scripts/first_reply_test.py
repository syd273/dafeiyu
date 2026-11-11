import sys, requests
from pathlib import Path
sys.path.insert(0, r"D:\大肥鱼\persona")
import persona_core
KEY = Path(r"D:\大肥鱼\deepseek-key.txt").read_text(encoding="utf-8").strip()
print("owner now:", repr(persona_core.owner_name()))
sysp = persona_core.build_system_prompt()
body = {"model":"deepseek-chat","messages":[{"role":"system","content":sysp},{"role":"user","content":"你好呀"}],"temperature":0.9,"max_tokens":150}
s = requests.Session(); s.trust_env=False
r = s.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json=body, timeout=60)
print("第一次回复:", r.json()["choices"][0]["message"]["content"].strip())