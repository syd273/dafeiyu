from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    skip_files = {"push_token.json", "trends_cache.json", "share_config.json"}''',
'''    skip_files = {
        "push_token.json", "push_credentials.json", "trends_cache.json",
        "share_config.json", ".bili_cache.json", ".douyin_cache.json",
        "music_cache.json", "safety_state.json",
    }
    skip_exts = {".py", ".pyc", ".mjs", ".js", ".ts", ".map", ".log", ".err", ".out"}''')
s = s.replace('''                if f.name in skip_files:
                    continue
                zf.write(f, f"{arc_root}/{rel}")''',
'''                if f.name in skip_files:
                    continue
                if f.suffix.lower() in skip_exts:
                    continue
                zf.write(f, f"{arc_root}/{rel}")''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("备份排除规则已收紧")