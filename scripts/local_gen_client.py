import sys, requests, time
sys.path.insert(0, r"D:\大肥鱼\anshiyu-server")
import local_llm
busy, who = local_llm.gpu_busy()
if busy:
    print("BUSY:", who); sys.exit(2)
body = {
  "model": "qwen2.5-coder:7b",
  "messages": [{"role": "system", "content": "你是严谨的 Python 程序员，只输出可直接运行的代码，不加代码围栏。"},
               {"role": "user", "content": open(r"D:\大肥鱼\scripts\p2_prompt.txt", encoding="utf-8").read()}],
  "stream": False, "think": False, "keep_alive": "30s",
  "options": {"temperature": 0.3, "num_predict": 2600, "num_ctx": 4096},
}
s = requests.Session(); s.trust_env = False
t = time.time()
r = s.post("http://127.0.0.1:11434/api/chat", json=body, timeout=300)
r.raise_for_status()
out = (r.json().get("message") or {}).get("content", "").strip()
open(r"D:\大肥鱼\life-core\docs\local_client_draft.py", "w", encoding="utf-8").write(out)
print("elapsed", round(time.time()-t,1), "chars", len(out))
print(out[:400])