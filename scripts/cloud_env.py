# -*- coding: utf-8 -*-
"""云服务器环境检查（root）"""
import paramiko

HOST = "192.236.173.41"
PORT = 2222
USER = "root"
PASSWORD = "BtaUmDTep2D5"


def main():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=40,
              banner_timeout=40, auth_timeout=40, allow_agent=False, look_for_keys=False)
    cmds = [
        "uname -a",
        "cat /etc/os-release | head -3",
        "node -v 2>/dev/null || echo no-node",
        "npm -v 2>/dev/null || echo no-npm",
        "python3 -V 2>/dev/null || echo no-python3",
        "pip3 -V 2>/dev/null || echo no-pip",
        "which git || echo no-git",
        "which nginx || echo no-nginx",
        "free -h | head -2",
        "df -h / | tail -1",
        "ss -lntp 2>/dev/null | head -10 || netstat -lntp 2>/dev/null | head -10",
        "cat /etc/ssh/sshd_config | grep -E '^Port|^PermitRootLogin|^PasswordAuthentication' || true",
    ]
    for cmd in cmds:
        stdin, stdout, stderr = c.exec_command(cmd, timeout=30)
        out = (stdout.read() + stderr.read()).decode("utf-8", "ignore").strip()
        print(f"$ {cmd}")
        print(out)
        print("-" * 50)
    c.close()


if __name__ == "__main__":
    main()
