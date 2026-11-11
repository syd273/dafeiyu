# -*- coding: utf-8 -*-
"""大肥鱼记忆维护脚本（规划 P1/P5）

功能：
  1. 事实抽取     从消息里抽取长期事实写入 facts 表
  2. 每日摘要     按天把对话压成 summaries（优先调用 DeepSeek，失败则本地压缩）
  3. 备份          SQLite 快照，滚动保留 14 天
  4. 10GB 预算监控 超 9GB 告警并按策略清理

用法：
    python scripts/maintain.py            # 全部执行
    python scripts/maintain.py facts      # 只抽事实
    python scripts/maintain.py summaries  # 只生成摘要
    python scripts/maintain.py backup     # 只备份
    python scripts/maintain.py budget     # 只看磁盘预算
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "memory"))
import kernel  # noqa: E402

DB = kernel.DB_PATH
SNAP = DB.parent / "snapshots"
MEDIA = DB.parent / "media"
LOGS = BASE / "logs"

BUDGET_GB = {
    "archive.db": 3.0,
    "media": 5.0,
    "snapshots": 1.5,
    "logs": 0.2,
}

FACT_PATTERNS = [
    (re.compile(r"我叫([\u4e00-\u9fa5A-Za-z0-9]{1,12})"), "我", "名字"),
    (re.compile(r"我今年([\u4e00-\u9fa5A-Za-z0-9]{1,8})岁"), "我", "年龄"),
    (re.compile(r"我喜欢(?:吃|看|玩|听|学)?([\u4e00-\u9fa5A-Za-z0-9]{1,12})"), "我", "喜欢"),
    (re.compile(r"我讨厌([\u4e00-\u9fa5A-Za-z0-9]{1,12})"), "我", "讨厌"),
    (re.compile(r"我想学([\u4e00-\u9fa5A-Za-z0-9]{1,12})"), "我", "想学"),
    (re.compile(r"我想要([\u4e00-\u9fa5A-Za-z0-9]{1,12})"), "我", "想要"),
    (re.compile(r"我(?:在|住在)([\u4e00-\u9fa5A-Za-z0-9]{2,12})"), "我", "所在地"),
    (re.compile(r"我的妈妈叫([\u4e00-\u9fa5A-Za-z0-9]{1,12})"), "妈妈", "名字"),
]


def get_conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


# ---------------- 1. 事实抽取 ----------------
def extract_facts() -> int:
    c = get_conn()
    added = 0
    try:
        done = {
            r["msg_id"]
            for r in c.execute("SELECT DISTINCT msg_id FROM facts WHERE msg_id IS NOT NULL")
        }
        rows = c.execute(
            "SELECT id, text FROM messages WHERE role='user' ORDER BY id DESC LIMIT 5000"
        ).fetchall()
        for r in rows:
            if r["id"] in done:
                continue
            text = r["text"] or ""
            for pat, subj, pred in FACT_PATTERNS:
                m = pat.search(text)
                if not m:
                    continue
                obj = m.group(1).strip()
                if len(obj) < 1:
                    continue
                exists = c.execute(
                    "SELECT 1 FROM facts WHERE subject=? AND predicate=? AND object=?",
                    (subj, pred, obj),
                ).fetchone()
                if exists:
                    continue
                c.execute(
                    """INSERT INTO facts(ts, subject, predicate, object, confidence, msg_id)
                       VALUES(?,?,?,?,?,?)""",
                    (r["id"] and time.time() or time.time(), subj, pred, obj, 0.7, r["id"]),
                )
                added += 1
        c.commit()
        return added
    finally:
        c.close()


# ---------------- 2. 每日摘要 ----------------
def _deepseek_key() -> str | None:
    try:
        p = BASE / "deepseek-key.txt"
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    cfg = BASE / "AstrBot" / "data" / "cmd_config.json"
    try:
        d = json.loads(cfg.read_text(encoding="utf-8-sig"))
        for src in d.get("provider_sources", []):
            for k in src.get("key", []):
                if k:
                    return k
    except Exception:
        pass
    return None


def _llm_summary(text: str, key: str) -> str | None:
    import urllib.request

    body = json.dumps(
        {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "把下面这段聊天记录压缩成 3-6 条要点，用第三人称，保留关键事实（人名、爱好、计划、情绪）。只输出要点，不要寒暄。",
                },
                {"role": "user", "content": text[:12000]},
            ],
            "max_tokens": 400,
            "temperature": 0.3,
        }
    ).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read().decode())
        return d["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _local_summary(lines: list[str]) -> str:
    head = []
    for ln in lines:
        t = ln.strip()
        if t and t not in head:
            head.append(t)
        if len(head) >= 6:
            break
    return "；".join(x[:40] for x in head)


def build_summaries(days: int = 30) -> int:
    c = get_conn()
    made = 0
    try:
        since = int(time.time()) - days * 86400
        rows = c.execute(
            "SELECT id, ts, role, text FROM messages WHERE ts>=? ORDER BY ts ASC",
            (since,),
        ).fetchall()
        if not rows:
            return 0
        groups: dict[str, list] = {}
        for r in rows:
            day = time.strftime("%Y-%m-%d", time.localtime(r["ts"]))
            groups.setdefault(day, []).append(r)
        key = _deepseek_key()
        for day, msgs in sorted(groups.items()):
            if len(msgs) < 8:
                continue
            exists = c.execute(
                "SELECT 1 FROM summaries WHERE kind='day' AND text LIKE ?", (f"[{day}]%",)
            ).fetchone()
            if exists:
                continue
            plain = "\n".join(
                f"{'我' if m['role']=='user' else '大肥鱼'}：{m['text']}" for m in msgs if m["text"]
            )
            text = _llm_summary(plain, key) if key else None
            if not text:
                text = _local_summary([m["text"] for m in msgs if m["text"]])
            text = f"[{day}] " + text
            c.execute(
                """INSERT INTO summaries(ts, kind, start_ts, end_ts, text, tokens)
                   VALUES(?,?,?,?,?,?)""",
                (int(time.time()), "day", msgs[0]["ts"], msgs[-1]["ts"], text,
                 max(1, len(text) // 2)),
            )
            made += 1
            time.sleep(0.4)
        c.commit()
        return made
    finally:
        c.close()


# ---------------- 3. 备份 ----------------
def backup() -> str:
    SNAP.mkdir(parents=True, exist_ok=True)
    target = SNAP / f"archive-{time.strftime('%Y%m%d-%H%M%S')}.db"
    src = sqlite3.connect(DB)
    dst = sqlite3.connect(target)
    src.backup(dst)
    dst.close()
    src.close()
    files = sorted(SNAP.glob("archive-*.db"), key=lambda p: p.stat().st_mtime)
    for old in files[:-14]:
        old.unlink(missing_ok=True)
    return target.name


# ---------------- 4. 10GB 预算监控 ----------------
def dir_size(p: Path) -> int:
    if not p.exists():
        return 0
    if p.is_file():
        return p.stat().st_size
    total = 0
    for f in p.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except Exception:
                pass
    return total


def budget() -> dict:
    items = {
        "archive.db": dir_size(DB),
        "media": dir_size(MEDIA),
        "snapshots": dir_size(SNAP),
        "logs": dir_size(LOGS),
    }
    out = {}
    total = 0
    for k, v in items.items():
        total += v
        limit = BUDGET_GB.get(k, 0) * 1024**3
        out[k] = {
            "used_mb": round(v / 1024**2, 1),
            "limit_mb": round(limit / 1024**2, 0),
            "pct": round(v / limit * 100, 1) if limit else 0,
        }
    out["total_gb"] = round(total / 1024**3, 3)
    out["limit_gb"] = sum(BUDGET_GB.values())
    # 超限清理：快照只留 14 份；日志只留 30 天
    files = sorted(SNAP.glob("archive-*.db"), key=lambda p: p.stat().st_mtime)
    for old in files[:-14]:
        old.unlink(missing_ok=True)
    cutoff = time.time() - 30 * 86400
    for f in LOGS.glob("*.log"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except Exception:
            pass
    return out


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "facts"):
        n = extract_facts()
        print(f"[facts] 新增 {n} 条")
    if what in ("all", "summaries"):
        n = build_summaries()
        print(f"[summaries] 新增 {n} 条")
    if what in ("all", "backup"):
        print(f"[backup] {backup()}")
    if what in ("all", "budget"):
        print("[budget] " + json.dumps(budget(), ensure_ascii=False))


if __name__ == "__main__":
    main()
