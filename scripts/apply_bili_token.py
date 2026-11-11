from pathlib import Path
import ast, json

p = Path(r"D:\大肥鱼\plugins\astrbot_plugin_anshiyu_proactive\main.py")
s = p.read_text(encoding="utf-8")

if "bili_mod" not in s:
    s = s.replace(
"""try:
    import retention as retention_mod
except Exception:
    retention_mod = None""",
"""try:
    import retention as retention_mod
except Exception:
    retention_mod = None
try:
    import bili as bili_mod
except Exception:
    bili_mod = None


def token_balance() -> float | None:
    try:
        key = KEY_PATH.read_text(encoding="utf-8").strip()
        sess = requests.Session()
        sess.trust_env = False
        r = sess.get("https://api.deepseek.com/user/balance",
                     headers={"Authorization": f"Bearer {key}"}, timeout=20)
        d = r.json()
        return float(d["balance_infos"][0]["total_balance"])
    except Exception:
        return None""")

    # tick 开头：余额检查
    s = s.replace(
"""        st = load_state()
        now = time.time()
        cands = self._available(cfg, st, now)""",
"""        st = load_state()
        now = time.time()

        # 饭钱（token 余额）检查
        try:
            chk_every = float(cfg.get("token_check_minutes", 60)) * 60
            if now - float(st.get("last_token_check", 0)) > chk_every:
                st["last_token_check"] = now
                save_state(st)
                bal = token_balance()
                if bal is not None and bal < float(cfg.get("token_low_threshold", 5.0)):
                    if now - float(st.get("last_token_alert", 0)) > float(cfg.get("token_alert_hours", 12)) * 3600:
                        msg = f"阿东……我的饭钱快没了（余额只剩 ¥{bal:.2f}），要不要给我充点 token 呀。"
                        if await self._send(msg):
                            st["last_token_alert"] = now
                            save_state(st)
                            logger.info("[anshiyu_proactive] 已提醒余额不足")
        except Exception as e:
            logger.warning(f"[anshiyu_proactive] 余额检查失败: {e}")

        cands = self._available(cfg, st, now)""")

    # bili 类型
    s = s.replace(
'        if pick["id"] == "life" and life_core is not None:',
'''        bili_video = None
        if pick["id"] == "bili" and bili_mod is not None:
            bili_video = bili_mod.random_video()
            if not bili_video:
                return
            hint = (f"你刚在B站刷到一个视频，标题是《{bili_video['title']}》，"
                    f"UP主是{bili_video['owner']}。想跟阿东分享，顺便说说你的感受。")
        if pick["id"] == "life" and life_core is not None:''')

    s = s.replace(
'        if await self._send(text):',
'''        if bili_video:
            text = text.rstrip() + "\\n" + bili_video["url"]
        if await self._send(text):''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("bili+token patched")

# life.json 加入 B 站活动
lp = Path(r"D:\大肥鱼\persona\life.json")
life = json.loads(lp.read_text(encoding="utf-8"))
ev = life.get("events", {})
ev.setdefault("evening", []).extend(["在B站刷到一个视频，笑了好久", "刷B站刷到忘记时间"])
ev.setdefault("night", []).append("躺床上刷B站，越刷越精神")
life["events"] = ev
lp.write_text(json.dumps(life, ensure_ascii=False, indent=2), encoding="utf-8")
print("life events updated")