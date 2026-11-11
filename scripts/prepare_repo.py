from pathlib import Path
import json

base = Path(r"D:\大肥鱼")

# 1) .gitignore 增加产物与签名
p = base / ".gitignore"
s = p.read_text(encoding="utf-8")
for line in ["dist/", "backups/", "signing/", "anshiyu-server/config.json", "persona/.bili_cache.json", "persona/.douyin_cache.json", "persona/music_cache.json", "*.bak*"]:
    if line not in s:
        s = s.rstrip() + "\n" + line
p.write_text(s, encoding="utf-8")
print(".gitignore 已更新")

# 2) 生成 config.example.json（token 占位、key 路径通用）
cfg = json.loads((base / "anshiyu-server" / "config.json").read_text(encoding="utf-8"))
cfg["token"] = "change-me-to-a-random-token"
cfg["deepseek_key_file"] = "deepseek-key.txt"
example = base / "anshiyu-server" / "config.example.json"
example.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("config.example.json 已生成")