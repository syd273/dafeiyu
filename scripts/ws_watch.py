# -*- coding: utf-8 -*-
"""模拟 App 在线：连接网关 WS，等待主动消息触发（最多等待 wait_sec 秒）"""
import asyncio
import json
import sys
import time

import websockets

WS_URL = "ws://127.0.0.1:8900/ws?token=anshiyu-app-2026"


async def main(wait_sec: int = 300):
    got = []
    async with websockets.connect(WS_URL) as ws:
        print(f"[ws] 已连接 {WS_URL}", flush=True)
        deadline = time.time() + wait_sec
        while time.time() < deadline:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=15)
            except asyncio.TimeoutError:
                continue
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            if msg.get("type") == "message" and msg.get("role") == "assistant":
                text = msg.get("text", "")
                got.append(text)
                print(f"[收到主动消息] {text}", flush=True)
                if len(got) >= 1:
                    break
    print(f"[ws] 结束，共收到 {len(got)} 条", flush=True)


if __name__ == "__main__":
    wait = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    asyncio.run(main(wait))
