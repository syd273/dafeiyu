import sys, requests
from pathlib import Path
sys.path.insert(0, r"D:\大肥鱼\persona")
import persona_core, bili
KEY = Path(r"D:\大肥鱼\deepseek-key.txt").read_text(encoding="utf-8").strip()
v = bili.random_video()
sysp = persona_core.build_system_prompt(memories=None, last_reply="")
sysp += ("\n\n你刚在B站刷到一个视频，标题是《" + v["title"] + "》，UP主是" + v["owner"] +
         "。想跟阿东分享，顺便说说你的感受。只输出消息本身，1-2句，口语。")
body = {"model": "deepseek-chat", "messages": [{"role": "system", "content": sysp},
        {"role": "user", "content": "（发给他）"}], "temperature": 0.9, "max_tokens": 120}
s = requests.Session(); s.trust_env = False
r = s.post("https://api.deepseek.com/v1/chat/completions",
           headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=60)
print("视频:", v["title"][:44], "| UP:", v["owner"])
print("她会说:", r.json()["choices"][0]["message"]["content"].strip())
print("链接:", v["url"])
rr = s.get("https://api.deepseek.com/user/balance", headers={"Authorization": f"Bearer {KEY}"}, timeout=20)
print("余额:", rr.json()["balance_infos"][0]["total_balance"])