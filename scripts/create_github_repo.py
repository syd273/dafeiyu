import subprocess, json, base64, requests
out = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                     capture_output=True, text=True, cwd=r"D:\大肥鱼").stdout
tok = ""
for line in out.splitlines():
    if line.startswith("password="):
        tok = line.split("=", 1)[1]
print("token 获取:", "成功" if tok else "失败")
if tok:
    h = {"Authorization": f"token {tok}", "User-Agent": "anshiyu", "Accept": "application/vnd.github+json"}
    r = requests.get("https://api.github.com/user", headers=h, timeout=20, proxies={"http": None, "https": None})
    print("用户:", r.json().get("login"))
    # 创建仓库（已存在则跳过）
    body = {"name": "anshiyu", "description": "安诗鱼 · 会生活、有记忆的 AI 陪伴（HarmonyOS）", "private": False, "auto_init": False}
    c = requests.post("https://api.github.com/user/repos", headers=h, json=body, timeout=20, proxies={"http": None, "https": None})
    print("创建仓库:", c.status_code, c.json().get("full_name") or c.json().get("message"))