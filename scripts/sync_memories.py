# -*- coding: utf-8 -*-
"""记忆自动同步器：监听记忆库新消息 → 用 DeepSeek 改写成安诗鱼的记忆 → 更新星图 JSON

每 20 秒检查一次，只处理新消息（增量）。
"""

import json
import sqlite3
import time
from pathlib import Path

import requests

DB = r"D:\大肥鱼\memory\archive.db"
OUT = Path(r"D:\大肥鱼\milky-way-3d\memory_stars.json")
STATE = Path(r"D:\大肥鱼\memory\.sync_state.json")
PERSONA_DIR = Path(r"D:\大肥鱼\persona")
KEY = Path(r"D:\大肥鱼\deepseek-key.txt").read_text(encoding="utf-8").strip()
URL = "https://api.deepseek.com/v1/chat/completions"
CHUNK = 16
INTERVAL = 20

SYSTEM = """你叫安诗鱼，是阿东的 AI 伙伴。下面是一段新的聊天记录。
请把这些内容转成「你所记住的事情」，用 JSON 数组输出。

规则：
1. 第三人称称呼阿东（"阿东"），第一人称"我"指你自己。
2. 每条记忆像你心里的一句话，带上你的心情，例如：
   - "他的名字叫阿东，我就这样称呼他吧。"
   - "阿东给我起名叫安诗鱼，我很开心。"
   - "阿东说发烧了还不吃消炎药，我很担心他。"
3. 重要事实单独记一条，例如："他说过对消炎药过敏，我记住了。"
4. emo 取值：开心 / 担心 / 着急 / 难过 / 平静 / 兴奋 / 生气 / 无语。
5. ts 用对应消息的时间戳。
只输出 JSON 数组，不要解释。格式：[{"ts":123,"text":"...","emo":"担心"}]"""


def load_out() -> list:
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_out(items: list):
    try:
        import sys
        if str(PERSONA_DIR) not in sys.path:
            sys.path.insert(0, str(PERSONA_DIR))
        import retention
        items = retention.annotate(items)
    except Exception as e:
        print('[sync] retention 失败:', e, flush=True)
    items.sort(key=lambda x: x.get("ts") or 0)
    for i, it in enumerate(items):
        it["id"] = i + 1
    OUT.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


def load_state() -> int:
    try:
        return int(json.loads(STATE.read_text(encoding="utf-8")).get("last_id", 0))
    except Exception:
        return 0


def save_state(last_id: int):
    STATE.write_text(json.dumps({"last_id": last_id}), encoding="utf-8")


def call_llm(msgs: list) -> list:
    text = "\n".join(
        f"[{m['ts']}] {'阿东' if m['role'] == 'user' else '我'}：{m['text']}"
        for m in msgs if m["text"]
    )
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text[:8000]},
        ],
        "temperature": 0.4,
        "max_tokens": 1200,
    }
    r = requests.Session()
    r.trust_env = False
    r = r.post(URL, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=90)
    r.raise_for_status()
    t = r.json()["choices"][0]["message"]["content"].strip()
    if t.startswith("```"):
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    s, e = t.find("["), t.rfind("]")
    return json.loads(t[s:e + 1])


def sync_life():
    """把她的生活状态与说说同步给星图应用"""
    import shutil
    src_dir = Path(r"D:\大肥鱼\persona")
    dst_dir = Path(r"D:\大肥鱼\milky-way-3d\life")
    dst_dir.mkdir(parents=True, exist_ok=True)
    # 当前状态快照
    try:
        import sys
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        import life_core
        (dst_dir / "status.json").write_text(json.dumps(life_core.current(), ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    try:
        import json as _json
        import sqlite3 as _sq2
        cc = _sq2.connect(BASE / "memory" / "archive.db")
        last_user = cc.execute("SELECT text, ts FROM messages WHERE role='user' ORDER BY id DESC LIMIT 1").fetchone()
        cc.close()
        if last_user and last_user[0] and life_core is not None:
            stl = life_core.load_state()
            if stl.get("last_applied_msg_ts") != last_user[1]:
                life_core.apply_message(last_user[0])
                stl = life_core.load_state()
                stl["last_applied_msg_ts"] = last_user[1]
                life_core.save_state(stl)
            life_core.mood_drift()
    except Exception:
        pass
    try:
        import json as _json
        life = _json.loads((src_dir / "life.json").read_text(encoding="utf-8"))
        (dst_dir / "schedule.json").write_text(_json.dumps(
            {"schedule": (life_core.merged_schedule() if life_core is not None else life.get("schedule", []))}, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    try:
        import sqlite3 as _sq
        _c = _sq.connect(BASE / "memory" / "archive.db")
        _n = _c.execute("SELECT COUNT(*) FROM messages WHERE role='user'").fetchone()[0]
        _c.close()
        if _n > 0 and life_core is not None:
            life_core.mark_started()
    except Exception:
        pass
    for name in ("life_state.json", "feed.json"):
        src = src_dir / name
        if src.exists():
            try:
                shutil.copy2(src, dst_dir / name)
            except Exception:
                pass

def tick() -> int:
    last = load_state()
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    rows = c.execute(
        "SELECT id, ts, role, text FROM messages WHERE id>? ORDER BY id ASC LIMIT 200", (last,)
    ).fetchall()
    c.close()
    if not rows:
        return 0
    msgs = [dict(r) for r in rows]
    new_items = load_out()
    added = 0
    for i in range(0, len(msgs), CHUNK):
        part = msgs[i:i + CHUNK]
        try:
            mems = call_llm(part)
        except Exception as e:
            print("LLM 失败:", e, flush=True)
            mems = []
        for m in mems:
            if not isinstance(m, dict) or not m.get("text"):
                continue
            t = str(m["text"]).replace("大肥鱼", "安诗鱼")
            new_items.append({
                "ts": int(m.get("ts") or part[0]["ts"]),
                "role": "memory",
                "emo": m.get("emo") or "平静",
                "text": t,
                "view": t,
                "speaker": "安诗鱼",
            })
            added += 1
    save_state(msgs[-1]["id"])
    if added:
        save_out(new_items)
    print(f"[sync] 新消息 {len(msgs)} 条 -> 新记忆 {added} 条，总计 {len(new_items)}", flush=True)
    return added


def main():
    print("[sync] 记忆自动同步已启动", flush=True)
    while True:
        try:
            tick()
            sync_life()
        except Exception as e:
            print("[sync] 异常:", e, flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
