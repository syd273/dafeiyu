# -*- coding: utf-8 -*-
"""性格效果测试：用当前人格提示词让 DeepSeek 生成几条回复，检查语气。"""

import json
import sys
from pathlib import Path

import requests

BASE = Path(r"D:\大肥鱼")
sys.path.insert(0, str(BASE / "persona"))
import persona_core  # noqa: E402

KEY = (BASE / "deepseek-key.txt").read_text(encoding="utf-8").strip()
URL = "https://api.deepseek.com/v1/chat/completions"

CASES = [
    ("认识一下，我叫阿东", "初次见面"),
    ("安诗鱼，我今天发烧了，还不能吃消炎药，我对消炎药过敏", "生病+过敏"),
    ("你在干嘛呢", "日常"),
    ("我今天有点想放弃", "情绪低落"),
    ("你喜欢我吗", "暧昧"),
    ("我今天夸你一句：你很好看", "被夸"),
]


def ask(system: str, user: str) -> str:
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.85,
        "max_tokens": 220,
    }
    sess = requests.Session(); sess.trust_env = False
    r = sess.post(URL, headers={"Authorization": f"Bearer {KEY}"}, json=body, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def main():
    for text, tag in CASES:
        persona_core.update_mood(text)
        sysp = persona_core.build_system_prompt(memories=None, last_reply="")
        try:
            reply = ask(sysp, text)
        except Exception as e:
            reply = f"<失败: {e}>"
        mood = persona_core.current_mood().get("mood")
        print(f"\n=== {tag} | 心情={mood} ===")
        print("阿东:", text)
        print("安诗鱼:", reply)


if __name__ == "__main__":
    main()
