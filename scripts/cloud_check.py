# -*- coding: utf-8 -*-
"""测试云服务器连接与环境"""
import sys

import paramiko

HOST = "192.236.173.41"
PORT = 2222
PASSWORD = "BtaUmDTep2D5"
USERS = ["root", "ubuntu", "centos", "admin", "debian"]


def try_user(user: str):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(HOST, port=PORT, username=user, password=PASSWORD, timeout=15,
                  allow_agent=False, look_for_keys=False)
        return c
    except Exception as e:
        print(f"[{user}] 失败: {e}")
        return None


def run(c, cmd: str) -> str:
    stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
    out = stdout.read().decode("utf-8", "ignore")
    err = stderr.read().decode("utf-8", "ignore")
    return (out + err).strip()


def main():
    for user in USERS:
        print(f"尝试 {user}@{HOST}:{PORT} ...")
        c = try_user(user)
        if not c:
            continue
        print(f"[OK] 已连接 {user}")
        for cmd in ["uname -a", "cat /etc/os-release | head -3", "node -v || echo no-node",
                    "python3 -V || echo no-python3", "which nginx || echo no-nginx",
                    "free -h | head -2", "df -h / | tail -1"]:
            print(f"$ {cmd}")
            print(run(c, cmd))
            print("-" * 40)
        c.close()
        return
    print("所有用户名都连接失败")


if __name__ == "__main__":
    main()
