from pathlib import Path
import ast, json

# 1) 网关：删除 /api/legacy/trigger 端点
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
start = s.find('@app.post("/api/legacy/trigger")')
if start >= 0:
    end = s.find('    finally:\n        _legacy_lock["running"] = False', start)
    if end >= 0:
        end = end + len('    finally:\n        _legacy_lock["running"] = False') + 2
        s = s[:start] + s[end:]
        p.write_text(s, encoding="utf-8")
        print("已移除手动触发端点")
    else:
        print("未找到端点结尾")
else:
    print("端点不存在")
ast.parse(s)
print("语法 OK")

# 2) 回滚测试传承：恢复第 1 代 + messages
bak = Path(r"D:\大肥鱼\memory\archive.db.bak_legacy")
db = Path(r"D:\大肥鱼\memory\archive.db")
if bak.exists():
    import shutil
    shutil.copy2(bak, db)
    print("已恢复 archive.db")
for f in ["gen_001.json"]:
    q = Path(r"D:\大肥鱼\memory\legacy") / f
    if q.exists():
        q.unlink()
        print("已删除", f)
st = Path(r"D:\大肥鱼\memory\legacy\state.json")
if st.exists():
    st.unlink()
    print("已重置 state.json")