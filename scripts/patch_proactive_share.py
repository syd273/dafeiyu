from pathlib import Path
import ast, json

p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

# 1) 插入媒体分享函数与手动触发接口（放在 share_douyin 之后）
anchor = '@app.post("/api/code")'
helper = '''async def _do_media_share(platform: str):
    """自主刷媒体并分享（B站/抖音），返回分享文本或 None。"""
    platform = "douyin" if platform == "douyin" else "bili"
    try:
        if platform == "bili":
            if bili is None:
                return None
            v = bili.random_video()
            if not v:
                return None
            system = persona_core.build_system_prompt(life=life_core.current())
            system += (f"\\n\\n你刚在B站刷到一个视频，标题是《{v['title']}》，UP主是{v['owner']}。"
                       "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-2句，口语。")
            text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200)
            if not text:
                return None
            text = text.rstrip() + "\\n" + v["url"]
            if life_bridge is not None:
                life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
            item = v
        else:
            if douyin is None:
                return None
            h = douyin.random_hot()
            if not h:
                return None
            system = persona_core.build_system_prompt(life=life_core.current())
            system += (f"\\n\\n你刚在抖音刷到一个热点：{h['title']}。"
                       "想跟阿东分享，顺便说说你的感受。只输出消息本身，1-3句，口语。")
            text = ask_llm(system, [{"role": "user", "content": "（发给他）"}], max_tokens=200)
            if not text:
                return None
            text = text.rstrip() + "\\n" + h["url"]
            if life_bridge is not None:
                life_bridge.event("share", f"在抖音刷到热点「{h['title']}」并分享了", "开心")
            item = h
        conn = kernel.connect()
        try:
            kernel.add_message(conn, text, role="assistant", platform="app", umo="app")
        finally:
            conn.close()
        await broadcast({"type": "message", "role": "assistant", "text": text, "ts": int(time.time())})
        return {"text": text, "item": item, "platform": platform}
    except Exception:
        return None


@app.post("/api/share/auto")
async def share_auto(token: str = Query(""), platform: str = Query("random")):
    """手动触发一次"自主刷媒体分享"（测试/演示用）"""
    auth(token)
    kind = platform if platform in ("bili", "douyin") else random.choice(["bili", "douyin"])
    r = await _do_media_share(kind)
    return {"ok": r is not None, **(r or {})}


@app.post("/api/code")'''
if '_do_media_share' not in s:
    s = s.replace(anchor, helper)
    print("helper added")

# 2) proactive_loop 支持 share_media 类型
old = '''            pick = types[int(now) % len(types)]
            life = life_core.current()'''
new = '''            pick = types[int(now) % len(types)]
            # 自主刷媒体分享（独立限频：每天最多 2 条，间隔 ≥180 分钟）
            if pick.get("id") == "share_media":
                share_day = time.strftime("%Y-%m-%d")
                if st.get("share_day") != share_day:
                    st["share_day"] = share_day
                    st["share_count"] = 0
                if int(st.get("share_count", 0)) >= 2:
                    continue
                if now - st.get("last_share", 0) < 180 * 60:
                    continue
                platform = random.choice(["bili", "douyin"])
                res = await _do_media_share(platform)
                if res:
                    st["share_count"] = int(st.get("share_count", 0)) + 1
                    st["last_share"] = int(now)
                    st["last_sent"] = int(now)
                    st["count"] = int(st.get("count", 0)) + 1
                    save_state(st)
                continue
            life = life_core.current()'''
if 'share_media' not in s:
    s = s.replace(old, new)
    print("proactive share added")

# 3) 需要 random 模块
if 'import random' not in s:
    s = s.replace('import requests', 'import random\nimport requests')
    print("random imported")

p.write_text(s, encoding="utf-8")
ast.parse(s)
print("app.py patched")

# 4) proactive.json 增加 share_media 类型
cfg_p = Path(r"D:\大肥鱼\persona\proactive.json")
cfg = json.loads(cfg_p.read_text(encoding="utf-8"))
ids = [t["id"] for t in cfg["types"]]
if "share_media" not in ids:
    cfg["types"].append({"id": "share_media", "window": [10, 22], "weight": 1.0,
                         "hint": "你刚刷到一个想分享的内容"})
    cfg_p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print("proactive.json updated")