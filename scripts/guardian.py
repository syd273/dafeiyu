# -*- coding: utf-8 -*-
"""QQ 安全守卫：监控 NapCat/AstrBot/星图，掉线保护，防频繁重登。

原则：
- 被踢/账号异常 → 绝不自动重登，只提醒，等阿东手动扫码
- 普通崩溃 → 冷却 30 分钟、每天最多重启 2 次
- 所有事件写日志
"""

import ctypes
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

BASE = Path(r"D:\大肥鱼")
CFG_PATH = BASE / "safety.json"
STATE_PATH = BASE / "memory" / "safety_state.json"
LOG_PATH = BASE / "logs" / "guardian.log"
NAP = BASE / "qq" / "napcat"


def cfg() -> dict:
    try:
        return json.loads(CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"restarts": [], "kicked_ts": 0, "alerted": 0}


def save_state(st: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")


def log(msg: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def popup(title: str, text: str):
    def _show():
        try:
            ctypes.windll.user32.MessageBoxW(0, text, title, 0x40000 | 0x40 | 0x1000)
        except Exception:
            pass
    threading.Thread(target=_show, daemon=True).start()


def proc_alive(name: str) -> bool:
    try:
        out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}"],
                             capture_output=True, text=True, errors="ignore").stdout
        return name.lower() in out.lower()
    except Exception:
        return False


def napcat_alive() -> bool:
    """只认 NapCat 自己的 node 进程（Adobe 等其它 node.exe 不算）"""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | "
             "Where-Object { $_.CommandLine -match 'napcat' } | Measure-Object | "
             "Select-Object -ExpandProperty Count"],
            capture_output=True, text=True, errors="ignore", timeout=20).stdout
        return int((out or "0").strip() or 0) > 0
    except Exception:
        return False


def established(port: int) -> bool:
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, errors="ignore").stdout
        return any(f":{port}" in ln and "ESTABLISHED" in ln for ln in out.splitlines())
    except Exception:
        return False


def kicked_recently() -> bool:
    """从 NapCat 日志里找被踢/异常下线记录"""
    pats = cfg().get("kick_patterns", [])
    logs = sorted(BASE.glob("logs/napcat*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        return False
    try:
        tail = logs[0].read_text(encoding="utf-8", errors="ignore")[-20000:]
    except Exception:
        return False
    return any(p in tail for p in pats)


ACCOUNT_OFF_PATTERNS = ["账号状态变更为离线", "Ban state forbit", "下线通知", "被强制下线", "退出登录", "账号异常"]
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


def start_napcat():
    try:
        subprocess.Popen(["cmd", "/c", "napcat.bat"], cwd=str(NAP),
                         creationflags=subprocess.CREATE_NO_WINDOW)
        log("已尝试启动 NapCat")
    except Exception as e:
        log(f"启动 NapCat 失败: {e}")


def start_astrbot():
    try:
        subprocess.Popen([r"D:\Python312\Scripts\astrbot.exe", "run"],
                         cwd=str(BASE / "AstrBot"),
                         creationflags=subprocess.CREATE_NO_WINDOW)
        log("已尝试启动 AstrBot")
    except Exception as e:
        log(f"启动 AstrBot 失败: {e}")


def health_report():
    """生成每日健康报告"""
    import json, sqlite3
    today = time.strftime("%Y-%m-%d")
    lines = [f"===== 安诗鱼健康报告 {today} ====="]
    lines.append(f"NapCat：{'在线' if (proc_alive('node.exe') and established(6199)) else '离线'}")
    lines.append(f"AstrBot：{'运行中' if proc_alive('astrbot.exe') else '未运行'}")
    lines.append(f"安全守卫：运行中")
    # 今日消息与记忆
    try:
        conn = sqlite3.connect(BASE / "memory" / "archive.db")
        start = int(time.mktime(time.strptime(today, "%Y-%m-%d")))
        n_msg = conn.execute("SELECT COUNT(*) FROM messages WHERE ts>=?", (start,)).fetchone()[0]
        n_user = conn.execute("SELECT COUNT(*) FROM messages WHERE ts>=? AND role='user'", (start,)).fetchone()[0]
        conn.close()
        lines.append(f"今日对话：{n_msg} 条（阿东 {n_user} 条）")
    except Exception as e:
        lines.append(f"今日对话：读取失败 {e}")
    try:
        stars = json.loads((BASE / "milky-way-3d" / "memory_stars.json").read_text(encoding="utf-8"))
        today_stars = sum(1 for x in stars if time.strftime("%Y-%m-%d", time.localtime(x.get("ts", 0))) == today)
        lines.append(f"今日新记忆星：{today_stars} 颗（总计 {len(stars)}）")
    except Exception:
        lines.append("记忆星：读取失败")
    try:
        st = state()
        lines.append(f"主动消息：今日 {st.get('count', 0)} 条（上次类型 {list(st.get('fired', {}).keys())[:3]}）")
        lines.append(f"安全事件：重启 {len(st.get('restarts', []))} 次，被踢 {1 if st.get('kicked_ts') else 0} 次")
    except Exception:
        pass
    lines.append("")
    text = "\n".join(lines)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with (BASE / "logs" / "health_report.log").open("a", encoding="utf-8") as f:
        f.write(text + "\n")
    log("已生成每日健康报告")
    if c.get("notify_popup", True):
        popup("安诗鱼 · 每日健康报告", text)

def main():
    c = cfg()
    interval = int(c.get("check_interval_seconds", 30))
    log("安全守卫已启动")
    c0 = cfg()
    report_hour = int(c0.get("health_report_hour", 21))
    reported_day = ""
    offline_since = 0
    while True:
        st = state()
        today = time.strftime("%Y-%m-%d")
        restarts = [t for t in st.get("restarts", []) if time.strftime("%Y-%m-%d", time.localtime(t)) == today]

        # 手动模式：不自动拉起 NapCat、不弹窗（用桌面「登录安诗鱼」手动登录）
        manual = bool(c.get("manual_napcat", False))

        # 账号层面：即使进程/连接还在，账号也可能离线或被限制
        offline_flag = watch_account_log(st)
        if offline_flag and not manual and time.time() - st.get("acct_alerted", 0) > 3600:
            st["acct_alerted"] = int(time.time())
            save_state(st)
            log("检测到账号离线/被限制（日志）")
            if c.get("notify_popup", True):
                popup("安诗鱼 · QQ 账号离线或受限",
                      "NapCat 进程还在，但账号状态显示离线或被限制（Ban state）。\n请打开手机 QQ 查看提示，重新扫码登录。")

        node_alive = napcat_alive()
        ws_up = established(6199)
        nap_up = node_alive and ws_up
        if manual and not nap_up:
            nap_up = True  # 手动模式下视为"无需处理"
        if not nap_up:
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
                                  "QQ 已掉线（可能是断网/被踢）。\n请用手机 QQ 扫描已打开的二维码页面。")
                        try:
                            import os
                            os.startfile("http://127.0.0.1:8098/qr.html")
                        except Exception:
                            pass
                elif kicked_recently():
                    if time.time() - st.get("kicked_ts", 0) > 3600:
                        st["kicked_ts"] = int(time.time())
                        save_state(st)
                        log("检测到被踢/账号异常：不自动重登，等待人工处理")
                        if c.get("notify_popup", True):
                            popup("安诗鱼 · QQ 已掉线",
                                  "QQ 可能被踢下线或异常。\n为避免封号，我不会自动重登。\n请手动在 NapCat 扫码登录。")
                else:
                    cooldown = float(c.get("restart_cooldown_minutes", 30)) * 60
                    last = restarts[-1] if restarts else 0
                    if len(restarts) < int(c.get("max_restarts_per_day", 2)) and time.time() - last > cooldown:
                        log("NapCat 掉线（非踢下线），执行一次受控重启")
                        start_napcat()
                        restarts.append(time.time())
                        st["restarts"] = restarts
                        save_state(st)
                        offline_since = 0
                    else:
                        log("NapCat 掉线但已达重启限额，等待人工处理")
                offline_since = 0 if offline_since and time.time() - offline_since > 3600 else offline_since
        else:
            offline_since = 0
            if st.get("restarts") or st.get("qr_alerted"):
                st["restarts"] = []
                st["qr_alerted"] = 0
                st["account_offline"] = False
                save_state(st)

        if not proc_alive("astrbot.exe"):
            log("AstrBot 未运行，尝试启动")
            start_astrbot()

        # 每日健康报告
        if time.localtime().tm_hour == report_hour and time.strftime("%Y-%m-%d") != reported_day:
            reported_day = time.strftime("%Y-%m-%d")
            try:
                health_report()
            except Exception as e:
                log(f"健康报告失败: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    main()
