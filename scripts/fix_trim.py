from pathlib import Path
p = Path(r"D:\大肥鱼\life-core\src\brain\episode.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("""function trimEpisodes() {
  try {
    const max = Number(options().maxEpisodes || 0);
    if (!max) return;
    const rows = allEpisodes();
    if (rows.length <= max) return;
    const keep = rows.slice(-max);
    const { EPISODE_FILE } = requirePaths();
    if (EPISODE_FILE) {
      fs.writeFileSync(EPISODE_FILE, keep.map((r) => JSON.stringify(r)).join('\\n') + '\\n', 'utf8');
    }
  } catch (e) { }
}""",
"""function trimEpisodes() {
  try {
    const max = Number(options().maxEpisodes || 0);
    if (!max) return;
    const rows = allEpisodes(); // 新 -> 旧
    if (rows.length <= max) return;
    const keep = rows.slice(0, max).reverse(); // 旧 -> 新
    fs.writeFileSync(EP_FILE, keep.map((r) => JSON.stringify(r)).join('\\n') + '\\n', 'utf8');
  } catch (e) { }
}""")
s = s.replace("""  fs.appendFileSync(EP_FILE, JSON.stringify(row) + '\\n', 'utf8');
  return row;
}""",
"""  fs.appendFileSync(EP_FILE, JSON.stringify(row) + '\\n', 'utf8');
  trimEpisodes();
  return row;
}""")
p.write_text(s, encoding="utf-8")
print("裁剪逻辑已修复")