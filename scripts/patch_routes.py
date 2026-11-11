from pathlib import Path
p = Path(r"D:\大肥鱼\life-core\src\http.mjs")
s = p.read_text(encoding="utf-8")
old = """        if (url.pathname === '/memories') {
          const limit = Math.min(200, Math.max(1, parseInt(url.searchParams.get('limit') || '10', 10) || 10));
          return send(res, 200, await handlers.getMemories(limit));
        }"""
new = """        if (url.pathname === '/memories') {
          const limit = Math.min(200, Math.max(1, parseInt(url.searchParams.get('limit') || '10', 10) || 10));
          return send(res, 200, await handlers.getMemories(limit));
        }
        if (url.pathname === '/recall') {
          const q = url.searchParams.get('q') || '';
          return send(res, 200, await handlers.recall(q));
        }
        if (url.pathname === '/diary') {
          return send(res, 200, await handlers.diary());
        }"""
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("routes added")
else:
    print("MISS")