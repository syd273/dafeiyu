```python
import urllib.request
import urllib.parse
import json

class LifeCoreClient:
    def __init__(self, base_url="http://127.0.0.1:8910", timeout=60):
        self.base_url = base_url
        self.timeout = timeout

    def _request(self, path, method="GET", data=None):
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        try:
            if method == "GET":
                response = urllib.request.urlopen(url, timeout=self.timeout)
            elif method == "POST":
                data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                response = urllib.request.urlopen(req, timeout=self.timeout)
            else:
                return {"ok": False, "error": "Unsupported method"}
            return {"ok": True, "data": json.loads(response.read().decode('utf-8'))}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def health(self) -> dict:
        return self._request("/health")

    def get_state(self) -> dict:
        return self._request("/state")

    def chat(self, text: str) -> dict:
        data = {"text": text}
        return self._request("/chat", method="POST", data=data)

    def event(self, kind: str, text: str, emo: str = "") -> dict:
        data = {"kind": kind, "text": text, "emo": emo}
        return self._request("/event", method="POST", data=data)

    def recall(self, query: str) -> dict:
        data = {"query": query}
        return self._request("/recall", method="POST", data=data)

    def diary(self) -> dict:
        return self._request("/diary")

    def facts(self, p: str = "", s: str = "", limit: int = 50) -> dict:
        params = {"p": p, "s": s, "limit": limit}
        return self._request(f"/facts?{urllib.parse.urlencode(params)}")

    def intents(self) -> dict:
        return self._request("/intents")

    def intent_done(self, intent_id: str) -> dict:
        data = {"intent_id": intent_id}
        return self._request("/intent_done", method="POST", data=data)

    def consolidate(self) -> dict:
        return self._request("/consolidate")
```