from pathlib import Path
p = Path(r"D:\大肥鱼\life-core\src\http.mjs")
s = p.read_text(encoding="utf-8")

s = s.replace("""        if (p === '/intents') return send(res, 200, await handlers.intents());""",
"""        if (p === '/intents') return send(res, 200, await handlers.intents());
        if (p === '/mode') return send(res, 200, await handlers.getMode());""")

s = s.replace("""        if (p === '/intent/done') return send(res, 200, await handlers.intentDone(String(body.id || '')));""",
"""        if (p === '/intent/done') return send(res, 200, await handlers.intentDone(String(body.id || '')));
        if (p === '/mode') return send(res, 200, await handlers.setMode(body));
        if (p === '/nightly/run') return send(res, 200, await handlers.nightly(body));""")

p.write_text(s, encoding="utf-8")
print("http patched")