# -*- coding: utf-8 -*-
"""Life Core Python 客户端（本地 qwen2.5-coder:7b 起草，人工审校修正版）

修正点：
1. 去掉 markdown 围栏
2. intent_done 路径改为 /intent/done，字段改为 id
3. consolidate 改为 POST
4. 统一 JSON 编码与异常处理
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


class LifeCoreClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8910", timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, path: str, method: str = "GET", data: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        body = None
        headers = {"Content-Type": "application/json"}
        if method == "POST":
            body = json.dumps(data or {}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return json.loads(e.read().decode("utf-8"))
            except Exception:
                return {"ok": False, "error": f"HTTP {e.code}"}
        except Exception as e:  # 网络/超时/解析
            return {"ok": False, "error": str(e)}

    def health(self) -> dict:
        return self._request("/health")

    def get_state(self) -> dict:
        return self._request("/state")

    def chat(self, text: str) -> dict:
        return self._request("/chat", method="POST", data={"text": text})

    def event(self, kind: str, text: str, emo: str = "") -> dict:
        return self._request("/event", method="POST", data={"kind": kind, "text": text, "emo": emo})

    def recall(self, query: str) -> dict:
        return self._request("/recall?" + urllib.parse.urlencode({"q": query}))

    def diary(self) -> dict:
        return self._request("/diary")

    def facts(self, p: str = "", s: str = "", limit: int = 50) -> dict:
        params = {"p": p, "s": s, "limit": limit}
        return self._request("/facts?" + urllib.parse.urlencode(params))

    def intents(self) -> dict:
        return self._request("/intents")

    def intent_done(self, intent_id: str) -> dict:
        return self._request("/intent/done", method="POST", data={"id": intent_id})

    def consolidate(self) -> dict:
        return self._request("/consolidate", method="POST", data={})

    def get_options(self) -> dict:
        return self._request("/options")

    def set_options(self, payload: dict) -> dict:
        return self._request("/options", method="POST", data=payload or {})


if __name__ == "__main__":
    c = LifeCoreClient()
    print(json.dumps(c.health(), ensure_ascii=False))
