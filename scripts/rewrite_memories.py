# -*- coding: utf-8 -*-
"""把原始对话重写成「安诗鱼的记忆」：
- 第三人称称呼他（知道他名字后就用名字）
- 带她的心情
- 重要事实单列一条
输出 memory_stars.json
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

import requests

BASE = Path(r"D:\大肥鱼")
DB = BASE / "memory" / "archive.db"
OUT = BASE / "milky-way-3d" / "memory_stars.json"
KEY = (BASE / "deepseek-key.txt").read_text(encoding="utf-8").strip()
URL = "https://api.deepseek.com/v1/chat/completions"

sys.path.insert(0, str(BASE / "persona"))
try:
    import persona_core  # noqa: E402
except Exception:
    persona_core = None


def names():
    """返回 (他, 名字或描述)"""
    owner = ""
    if persona_core is not None:
        owner = persona_core.owner_name()
    return owner, (owner or "他")


def system_prompt() -> str:
    owner, desc = names()
    ex2 = f'"{desc}给我起名叫安诗鱼，我很开心。"' if owner else '"他给我起名叫安诗鱼，我很开心。"'
    ex3 = '"他说过对消炎药过敏，我记住了。"'
    return f"""你叫安诗鱼，是{desc}的 AI 伙伴。下面是{desc}和你的聊天记录（按时间顺序）。
请把这段对话转成「你所记住的事情」：

规则：
1. 用第三人称称呼他（"{desc}"），用第一人称"我"指你自己。
2. 每条记忆像你心里的一句话，带上你的感受/心情，例如：
   - "他的名字叫{desc}，我就这样称呼他吧。"（如果聊天里出现名字）
   - {ex2}
   - "他说他发烧了，还不吃消炎药，我很担心他。"
3. 重要事实（名字、过敏、地址、计划、喜好、约定等）单独记一条，例如：{ex3}
4. 每条记忆都要带 emo 字段，取值为：开心 / 担心 / 着急 / 难过 / 平静 / 兴奋 / 生气 / 无语。
5. ts 用你记住的那条消息的时间戳。
只输出 JSON 数组，不要任何解释。格式：
[{{"ts": 1793..., "text": "...", "emo": "担心"}}]"""


def call(chunk):
    owner, _ = names()
    speaker = owner or "他"
    msg = "\n".join(
        f"[{m['ts']}] {'我' if m['role'] != 'user' else speaker}：{m['text']}"
        for m in chunk if m["text"]
    )
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": msg[:9000]},
        ],
        "temperature": 0.4,
        "max_tokens": 1500,
    }
    s = requests.Session()
    s.trust_env = False
    r = s.post(URL, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=120)
    r.raise_for_status()
    txt = r.json()["choices"][0]["message"]["content"].strip()
    if txt.startswith("```"):
        txt = txt.split("```")[1]
        if txt.startswith("json"):
            txt = txt[4:]
    start = txt.find("[")
    end = txt.rfind("]")
    return json.loads(txt[start:end + 1])


def main():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    rows = c.execute(
        "SELECT id, ts, role, text FROM messages WHERE text IS NOT NULL AND text != '' ORDER BY ts ASC"
    ).fetchall()
    c.close()
    msgs = [dict(r) for r in rows]

    CHUNK = 24
    out = []
    for i in range(0, len(msgs), CHUNK):
        chunk = msgs[i:i + CHUNK]
        try:
            mems = call(chunk)
        except Exception as e:
            print(f"chunk {i} 失败: {type(e).__name__} {e}", flush=True)
            continue
        for m in mems:
            if not isinstance(m, dict) or not m.get("text"):
                continue
            out.append({
                "id": len(out) + 1,
                "ts": int(m.get("ts") or chunk[0]["ts"]),
                "role": "memory",
                "emo": m.get("emo") or "平静",
                "text": m["text"],
                "view": m["text"],
                "speaker": "安诗鱼",
            })
        print(f"chunk {i // CHUNK + 1}/{(len(msgs) - 1) // CHUNK + 1} -> 累计 {len(out)} 条记忆", flush=True)
        time.sleep(0.5)

    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"完成：{len(out)} 条记忆 -> {OUT}")


if __name__ == "__main__":
    main()
