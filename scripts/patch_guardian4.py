from pathlib import Path
import ast

p = Path(r"D:\大肥鱼\scripts\guardian.py")
s = p.read_text(encoding="utf-8")

old_line = '        nap_up = proc_alive("node.exe") and established(6199)'
new_line = '        node_alive = proc_alive("node.exe")\n        ws_up = established(6199)\n        nap_up = node_alive and ws_up'
s = s.replace(old_line, new_line)

old_block = '''        if not nap_up:
            if offline_since == 0:
                offline_since = time.time()
            down_min = (time.time() - offline_since) / 60
            if down_min >= float(c.get("offline_alert_minutes", 5)):
                if kicked_recently():'''
new_block = '''        if not nap_up:
            if offline_since == 0:
                offline_since = time.time()
            down_min = (time.time() - offline_since) / 60
            if down_min >= float(c.get("offline_alert_minutes", 5)):
                if node_alive and not ws_up:
                    if time.time() - st.get("qr_alerted", 0) > 600:
                        st["qr_alerted"] = int(time.time())
                        save_state(st)
                        log("NapCat 在线但未连接：需要扫码登录，自动打开二维码页")
                        if c.get("notify_popup", True):
                            popup("安诗鱼 · 需要扫码登录",
                                  "QQ 已掉线（可能是断网/被踢）。\\n请用手机 QQ 扫描已打开的二维码页面。")
                        try:
                            import os
                            os.startfile("http://127.0.0.1:8098/qr.html")
                        except Exception:
                            pass
                elif kicked_recently():'''
s = s.replace(old_block, new_block)

old_tail = '''        else:
            offline_since = 0'''
new_tail = '''        else:
            offline_since = 0
            if st.get("restarts") or st.get("qr_alerted"):
                st["restarts"] = []
                st["qr_alerted"] = 0
                st["account_offline"] = False
                save_state(st)'''
s = s.replace(old_tail, new_tail)

p.write_text(s, encoding="utf-8")
ast.parse(s)
print("guardian fixed ok")