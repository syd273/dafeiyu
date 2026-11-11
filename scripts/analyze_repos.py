from pathlib import Path
import re, json
base = Path(r"D:\大肥鱼\research")
for repo in ("dsh-dafeiyu-life", "dsh-feiyu"):
    root = base / repo
    js = [p for p in root.rglob("*") if p.suffix in (".js", ".mjs") and p.is_file()]
    dsh = []
    pure = []
    for p in js:
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "@deepseek-ai/" in t:
            dsh.append(p)
        else:
            pure.append(p)
    print(f"===== {repo} =====")
    print(f"JS 文件: {len(js)} | 依赖 @deepseek-ai: {len(dsh)} | 纯 JS: {len(pure)}")
    if repo == "dsh-feiyu":
        for sub in ("tools/brain", "tools/lib"):
            d = root / sub
            if d.exists():
                print(f"--- {sub} ---")
                for p in sorted(d.glob("*")):
                    if p.is_file():
                        print(f"  {p.name} {p.stat().st_size//1024}KB")
    if repo == "dsh-dafeiyu-life":
        docs = root / "docs"
        if docs.exists():
            print("--- docs ---")
            for p in sorted(docs.rglob("*.md"))[:20]:
                print("  " + str(p.relative_to(root)))