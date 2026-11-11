import sys, json, random
from pathlib import Path
sys.path.insert(0, r"D:\大肥鱼\persona")
import persona_core
import requests
BASE = Path(r"D:\大肥鱼")
KEY = (BASE/"deepseek-key.txt").read_text(encoding="utf-8").strip()
hints = {
 "早安": "早安，刚醒，想跟他说句话",
 "午饭": "提醒他吃饭，别饿着",
 "学习进度": "问问他之前说要学的东西/要考的东西进展，语气别像监督",
 "晚间": "问问他今天过得怎么样，累不累",
 "生病跟进": "他之前说发烧/过敏，关心一下好点没",
 "久未联系": "很久没聊了，说一句想他",
}
mem = ["阿东说他今天开始准备考试了，我有点心疼他。"]
s = requests.Session(); s.trust_env = False
for tag, hint in hints.items():
    persona_core.update_mood(tag)
    sysp = persona_core.build_system_prompt(memories=mem, last_reply="")
    sysp += ("\n\n现在你要主动给阿东发一条消息。" + hint +
             "\n要求：只输出这一条消息本身，1-2 句，口语，像突然想到他；不要解释、不要引号。")
    body = {"model":"deepseek-chat","messages":[{"role":"system","content":sysp},{"role":"user","content":"（现在主动发一条）"}],"temperature":0.9,"max_tokens":100}
    try:
        r = s.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization":f"Bearer {KEY}"}, json=body, timeout=60)
        t = r.json()["choices"][0]["message"]["content"].strip().strip('"“”')
    except Exception as e:
        t = f"<失败 {e}>"
    print(f"[{tag}] {t}")