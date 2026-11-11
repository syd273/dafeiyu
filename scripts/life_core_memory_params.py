from pathlib import Path

# 1) config.mjs 加记忆参数
p = Path(r"D:\大肥鱼\life-core\src\config.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("const DEFAULTS = { memoryMode: 'decay', nightlyHour: 3, nightlyMinute: 30 };",
"const DEFAULTS = {\n  memoryMode: 'decay',\n  nightlyHour: 3,\n  nightlyMinute: 30,\n  halfLifeDays: 1.08,   // 记忆半衰期（天）\n  maxEpisodes: 0,       // 最多保留情景数（0 = 不限）\n  nightlyReflect: true, // 夜间是否巩固/反思\n};")
s = s.replace("""export function setOptions(patch = {}) {
  const next = { ...options(), ...patch };
  if (!['decay', 'full'].includes(next.memoryMode)) next.memoryMode = 'decay';""",
"""export function setOptions(patch = {}) {
  const next = { ...options(), ...patch };
  if (!['decay', 'full'].includes(next.memoryMode)) next.memoryMode = 'decay';
  next.halfLifeDays = Math.min(30, Math.max(0.1, Number(next.halfLifeDays) || 1.08));
  next.maxEpisodes = Math.max(0, Number(next.maxEpisodes) || 0);""")
p.write_text(s, encoding="utf-8")
print("config.mjs 已更新")

# 2) recall.mjs 参数化半衰期
p = Path(r"D:\大肥鱼\life-core\src\brain\recall.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("function recencyScore(ts, now) {\n  const dt = Math.max(0, now - Number(ts || 0));\n  return Math.exp(-dt / HALF_LIFE_MS);\n}",
"function recencyScore(ts, now, halfLifeMs = HALF_LIFE_MS) {\n  const dt = Math.max(0, now - Number(ts || 0));\n  return Math.exp(-dt / Math.max(1, halfLifeMs));\n}")
s = s.replace("export function recallEpisodes(episodes = [], { query = '', now = Date.now(), weights = {}, mode = 'decay' } = {}) {",
"export function recallEpisodes(episodes = [], { query = '', now = Date.now(), weights = {}, mode = 'decay', halfLifeDays = 0 } = {}) {\n  const halfLifeMs = halfLifeDays > 0 ? halfLifeDays * 86400000 : HALF_LIFE_MS;")
s = s.replace("    const rec = recencyScore(ep.ts, now);",
"    const rec = recencyScore(ep.ts, now, halfLifeMs);")
p.write_text(s, encoding="utf-8")
print("recall.mjs 已更新")

# 3) episode.mjs 上限裁剪
p = Path(r"D:\大肥鱼\life-core\src\brain\episode.mjs")
s = p.read_text(encoding="utf-8")
if "maxEpisodes" not in s:
    s = s.replace("import fs from 'node:fs';",
"""import fs from 'node:fs';
import { options } from '../config.mjs';""")
    s = s.replace("export function appendEpisode({ text, kind = 'event', emo = '', ts = Date.now(), meta = {} }) {",
"""function trimEpisodes() {
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
}

export function appendEpisode({ text, kind = 'event', emo = '', ts = Date.now(), meta = {} }) {""")
    p.write_text(s, encoding="utf-8")
    print("episode.mjs 已加裁剪（需检查 requirePaths）")