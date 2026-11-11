from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "/api/backup/export" not in s:
    s = s.replace('LEGACY_DIR = BASE / "memory" / "legacy"',
'''BACKUP_DIR = BASE / "backups"


@app.post("/api/backup/export")
async def backup_export(token: str = Query("")):
    """打包记忆/聊天/传承为 zip（含隐私，妥善保存）"""
    auth(token)
    import zipfile
    from datetime import datetime
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"anshiyu-backup-{stamp}.zip"
    target = BACKUP_DIR / name
    include_dirs = [
        ("memory", BASE / "memory"),
        ("persona", BASE / "persona"),
        ("life-core/data", BASE / "life-core" / "data"),
    ]
    skip_names = {"qq", "logs", "research", "downloads", "node_modules", "__pycache__", "backups"}
    skip_files = {"push_token.json", "trends_cache.json", "share_config.json"}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc_root, src in include_dirs:
            if not src.exists():
                continue
            for f in src.rglob("*"):
                if not f.is_file():
                    continue
                rel = f.relative_to(src)
                if any(part in skip_names for part in rel.parts):
                    continue
                if f.name in skip_files:
                    continue
                zf.write(f, f"{arc_root}/{rel}")
    size = target.stat().st_size if target.exists() else 0
    return {"ok": True, "file": name, "size": size,
            "path": str(target), "at": int(time.time())}


@app.get("/api/backup/list")
async def backup_list(token: str = Query("")):
    auth(token)
    items = []
    if BACKUP_DIR.exists():
        for f in sorted(BACKUP_DIR.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
            items.append({"file": f.name, "size": f.stat().st_size,
                          "at": int(f.stat().st_mtime)})
    return {"ok": True, "items": items}


LEGACY_DIR = BASE / "memory" / "legacy"''')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("备份接口已加")
else:
    print("已存在")