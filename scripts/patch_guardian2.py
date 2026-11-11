from pathlib import Path
import ast

p = Path(r"D:\大肥鱼\scripts\guardian.py")
s = p.read_text(encoding="utf-8")

if "watch_account_log" not in s:
    s = s.replace("def start_napcat():", '''ACCOUNT_OFF_PATTERNS = ["账号状态变更为离线", "Ban state forbit", "下线通知", "被强制下线", "退出登录", "账号异常"]
ACCOUNT_ON_PATTERNS = ["登录成功", "已登录", "账号状态变更为在线"]


def watch_account_log(st: dict) -> bool:
    """读取 NapCat 新增日志，判断账号是否离线/被限制"""
    logs = sorted(BASE.glob("logs/napcat*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not logs:
        return st.get("account_offline", False)
    p = logs[0]
    key, size = str(p), p.stat().st_size
    prev = st.get("nap_log", {})
    offline = bool(st.get("account_offline", False))
    try:
        if prev.get("file") == key and prev.get("size", 0) <= size:
            with p.open("r", encoding="utf-8", errors="ignore") as f:
                f.seek(prev["size"])
                chunk = f.read()
            if any(x in chunk for x in ACCOUNT_OFF_PATTERNS):
                offline = True
            if any(x in chunk for x in ACCOUNT_ON_PATTERNS):
                offline = False
        st["nap_log"] = {"file": key, "size": size}
        st["account_offline"] = offline
    except Exception:
        pass
    return offline


def start_napcat():''')

    s = s.replace("        nap_up = proc_alive(\"node.exe\") and established(6199)",
'''        # 账号层面：即使进程/连接还在，账号也可能离线或被限制
        offline_flag = watch_account_log(st)
        if offline_flag and time.time() - st.get("acct_alerted", 0) > 3600:
            st["acct_alerted"] = int(time.time())
            save_state(st)
            log("检测到账号离线/被限制（日志）")
            if c.get("notify_popup", True):
                popup("安诗鱼 · QQ 账号离线或受限",
                      "NapCat 进程还在，但账号状态显示离线或被限制（Ban state）。\\n请打开手机 QQ 查看提示，重新扫码登录。")

        nap_up = proc_alive("node.exe") and established(6199)''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("guardian patched")