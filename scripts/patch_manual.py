from pathlib import Path
import ast, re
# 1) ps1 去掉 NapCat 段
p = Path(r"D:\大肥鱼\记忆星图.ps1")
s = p.read_text(encoding="utf-8-sig")
start = s.find("if (-not (Get-CimInstance Win32_Process -Filter \"Name='node.exe'\"")
end = s.find("$edge = 'C:\\Program Files")
if start >= 0 and end > start:
    s = s[:start] + "# NapCat：开机不自动登录（需要时用桌面「登录安诗鱼」）\n\n" + s[end:]
    p.write_text(s, encoding="utf-8-sig")
    print("ps1 cleaned")
else:
    print("ps1 MISS", start, end)

# 2) guardian 尊重 manual_napcat：不自动拉起、不弹窗
p = Path(r"D:\大肥鱼\scripts\guardian.py")
s = p.read_text(encoding="utf-8")
if "manual_napcat" not in s:
    s = s.replace('''        # 账号层面：即使进程/连接还在，账号也可能离线或被限制
        offline_flag = watch_account_log(st)''',
'''        # 手动模式：不自动拉起 NapCat、不弹窗（用桌面「登录安诗鱼」手动登录）
        manual = bool(c.get("manual_napcat", False))

        # 账号层面：即使进程/连接还在，账号也可能离线或被限制
        offline_flag = watch_account_log(st)''')
    s = s.replace('        if offline_flag and time.time() - st.get("acct_alerted", 0) > 3600:',
                  '        if offline_flag and not manual and time.time() - st.get("acct_alerted", 0) > 3600:')
    # 主循环：手动模式下掉线不重启不弹窗
    s = s.replace('        nap_up = node_alive and ws_up',
                  '        nap_up = node_alive and ws_up\n        if manual and not nap_up:\n            nap_up = True  # 手动模式下视为"无需处理"')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("guardian manual ok")