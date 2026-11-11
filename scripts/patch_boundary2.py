from pathlib import Path
p = Path(r"D:\大肥鱼\docs\项目边界-不与校枢冲突.md")
s = p.read_text(encoding="utf-8")
if "用户授权" not in s:
    s += """

## 五、用户授权：空闲时可借 qwen3.5:9b

用户明确授权：**校枢不用 qwen3.5:9b 时，安诗鱼可以调用**。

实现：`anshiyu-server/local_llm.py`
1. 调用前查 `http://127.0.0.1:11434/api/ps`，有模型加载 → 判定"校枢在用"，直接放弃
2. 空闲才发请求，`keep_alive=30s`，用完自动卸载，显存还给校枢
3. qwen3.5:9b 是思考模型，必须 `"think": false`，否则 content 为空
4. 失败不重试、不抢占；云端（DeepSeek）仍是默认主路径，本地只做兜底
5. bge-m3 向量借调同理（`try_local_embed`），默认未启用

实测：
- 校枢占用时：`try_local_chat` 返回 None（不打扰）
- 校枢空闲时：返回正常回复「在的，摸摸头，先歇会儿。要不要我给你讲个笑话逗逗乐？」
"""
    p.write_text(s, encoding="utf-8")
    print("boundary updated")
else:
    print("already")