# -*- coding: utf-8 -*-
"""Life Core 桥接层（网关调用）

设计：同步、短超时（8s）、绝不抛异常；Life Core 不可用时降级为空值，不影响主聊天。
本地模型起草版本把同步客户端误当异步、方法名也不对，此版为人工重写。
"""

from __future__ import annotations

try:
    from life_core_client import LifeCoreClient
except Exception:  # 允许独立导入
    LifeCoreClient = None  # type: ignore

_client = None


def _client_get():
    global _client
    if _client is None and LifeCoreClient is not None:
        _client = LifeCoreClient(timeout=8)
    return _client


def state() -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.get_state()
        return r if r.get("ok") else None
    except Exception:
        return None


def recall(query: str) -> list[dict]:
    try:
        c = _client_get()
        if c is None:
            return []
        r = c.recall(query) or {}
        return r.get("items") or []
    except Exception:
        return []


def event(kind: str, text: str, emo: str = "") -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.event(kind, text, emo)
        return r if r.get("ok") else None
    except Exception:
        return None


def facts(limit: int = 20) -> list[dict]:
    try:
        c = _client_get()
        if c is None:
            return []
        r = c.facts(limit=limit) or {}
        return r.get("items") or []
    except Exception:
        return []


def intents() -> list[dict]:
    try:
        c = _client_get()
        if c is None:
            return []
        r = c.intents() or {}
        return r.get("items") or []
    except Exception:
        return []


def diary() -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.diary()
        return r if r.get("ok") else None
    except Exception:
        return None


def consolidate() -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.consolidate()
        return r if r.get("ok") else None
    except Exception:
        return None


def options() -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.get_options()
        return r if r.get("ok") else None
    except Exception:
        return None


def set_options(payload: dict) -> dict | None:
    try:
        c = _client_get()
        if c is None:
            return None
        r = c.set_options(payload or {})
        return r if r.get("ok") else None
    except Exception:
        return None


def available() -> bool:
    return state() is not None
