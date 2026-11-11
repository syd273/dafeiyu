# -*- coding: utf-8 -*-
"""本地模型借调（用户授权：校枢不用时可用 qwen3.5:9b）

安全规则：
1. 调用前必须查 Ollama /api/ps：只要有任何模型已加载（校枢在用）→ 不调用
2. 调用时 keep_alive 很短（默认 60s），用完自动卸载，把显存还给校枢
3. 绝不主动加载/卸载别人的模型；失败就放弃，不重试抢占
"""

from __future__ import annotations

import requests

OLLAMA = "http://127.0.0.1:11434"
MODEL = "qwen3.5:9b"
KEEP_ALIVE = "30s"


def _sess() -> requests.Session:
    s = requests.Session()
    s.trust_env = False
    return s


def gpu_busy() -> tuple[bool, str]:
    """返回 (是否被占用, 占用说明)"""
    try:
        s = _sess()
        r = s.get(f"{OLLAMA}/api/ps", timeout=5)
        data = r.json()
        models = data.get("models") or []
        if models:
            names = ", ".join(m.get("name", "?") for m in models)
            return True, names
        return False, ""
    except Exception as e:
        # 查不到就当忙，宁可不借
        return True, f"ps 查询失败: {e}"


def try_local_chat(system: str, messages: list[dict], max_tokens: int = 400) -> str | None:
    """校枢空闲时借用 qwen3.5:9b；否则返回 None"""
    busy, who = gpu_busy()
    if busy:
        return None
    try:
        s = _sess()
        body = {
            "model": MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "think": False,          # qwen3.5 是思考模型，关掉思考否则 content 为空
            "keep_alive": KEEP_ALIVE,
            "options": {"temperature": 0.9, "num_predict": max_tokens, "num_ctx": 4096},
        }
        r = s.post(f"{OLLAMA}/api/chat", json=body, timeout=120)
        r.raise_for_status()
        data = r.json()
        return (data.get("message") or {}).get("content", "").strip() or None
    except Exception:
        return None


def try_local_embed(texts: list[str]) -> list[list[float]] | None:
    """校枢空闲时借用 bge-m3 做向量（同样短租借）"""
    busy, _ = gpu_busy()
    if busy:
        return None
    try:
        s = _sess()
        r = s.post(f"{OLLAMA}/api/embed",
                   json={"model": "bge-m3", "input": texts, "keep_alive": KEEP_ALIVE}, timeout=60)
        r.raise_for_status()
        return r.json().get("embeddings")
    except Exception:
        return None
