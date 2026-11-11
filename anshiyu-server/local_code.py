# -*- coding: utf-8 -*-
"""本地代码助手：写代码时交给 qwen3.5:9b（校枢空闲时才借）。

用法（命令行）：
    python local_code.py "写一个 FastAPI 上传接口" [上下文文件]
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).parent
for p in (str(BASE),):
    if p not in sys.path:
        sys.path.insert(0, p)

import local_llm  # noqa: E402

CODE_SYSTEM = """你是一个严谨的程序员。根据需求写出可直接运行的代码。
要求：
1. 只输出代码，不要解释（除非用户要求）
2. 代码要完整、能直接运行
3. 符合目标语言的惯例
"""


def write_code(instruction: str, context: str = "", language: str = "") -> str | None:
    """借用本地 qwen3.5:9b 写代码；校枢占用时返回 None"""
    parts = [CODE_SYSTEM]
    if language:
        parts.append(f"目标语言：{language}")
    if context:
        parts.append("已有上下文：\n" + context[:4000])
    system = "\n\n".join(parts)
    messages = [{"role": "user", "content": instruction}]
    return local_llm.try_local_chat(system, messages, max_tokens=1200)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python local_code.py <需求> [上下文文件路径]")
        raise SystemExit(1)
    instr = sys.argv[1]
    ctx = ""
    if len(sys.argv) >= 3:
        p = Path(sys.argv[2])
        if p.exists():
            ctx = p.read_text(encoding="utf-8", errors="ignore")
    busy, who = local_llm.gpu_busy()
    if busy:
        print(f"[busy] 校枢正在使用本地模型（{who}），本次不借调")
        raise SystemExit(2)
    out = write_code(instr, ctx)
    if not out:
        print("[fail] 本地模型调用失败")
        raise SystemExit(3)
    print(out)
