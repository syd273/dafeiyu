from pathlib import Path

# ===== server.mjs：halfLifeDays + 反思开关 + options handlers =====
p = Path(r"D:\大肥鱼\life-core\src\server.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("const hits = recallEpisodes(episodes(), { query: t, mode: memoryMode() });",
              "const hits = recallEpisodes(episodes(), { query: t, mode: memoryMode(), halfLifeDays: options().halfLifeDays });")
s = s.replace("const hits = recallEpisodes(episodes(), { query: String(query || ''), mode: memoryMode() });",
              "const hits = recallEpisodes(episodes(), { query: String(query || ''), mode: memoryMode(), halfLifeDays: options().halfLifeDays });")
s = s.replace("""  async nightly(payload = {}) {
    const cons = consolidate({ ownerName: String(payload?.ownerName || '阿东') });""",
"""  async nightly(payload = {}) {
    const opts = options();
    const cons = opts.nightlyReflect === false
      ? { processed: 0, skipped: true }
      : consolidate({ ownerName: String(payload?.ownerName || '阿东') });""")
s = s.replace("""  async setMode(payload = {}) {""",
"""  async getOptions() {
    return { ok: true, ...options() };
  },

  async setOptions(payload = {}) {
    const patched = setOptions({ ...payload });
    if (patched.memoryMode === 'full') episodeCache = allEpisodes();
    return { ok: true, ...patched };
  },

  async setMode(payload = {}) {""")
p.write_text(s, encoding="utf-8")
print("server.mjs 已更新")

# ===== http.mjs：/options 路由 =====
p = Path(r"D:\大肥鱼\life-core\src\http.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("if (p === '/mode') return send(res, 200, await handlers.getMode());",
"""if (p === '/mode') return send(res, 200, await handlers.getMode());
  if (p === '/options') return send(res, 200, await handlers.getOptions());""")
s = s.replace("if (p === '/mode') return send(res, 200, await handlers.setMode(body));",
"""if (p === '/mode') return send(res, 200, await handlers.setMode(body));
  if (p === '/options') return send(res, 200, await handlers.setOptions(body));""")
p.write_text(s, encoding="utf-8")
print("http.mjs 已更新")