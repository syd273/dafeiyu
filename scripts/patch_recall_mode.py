from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\life-core\src\brain\recall.mjs")
s = p.read_text(encoding="utf-8")

# 增加 mode 参数：full 模式不衰减、全量保留、上限提高
s = s.replace('''export function recallEpisodes(episodes = [], { query = '', now = Date.now(), weights = {} } = {}) {
  const w = { ...DEFAULT_WEIGHTS, ...weights };''',
'''export function recallEpisodes(episodes = [], { query = '', now = Date.now(), weights = {}, mode = 'decay' } = {}) {
  const full = mode === 'full';
  const w = { ...DEFAULT_WEIGHTS, ...(full ? { recency: 0 } : {}), ...weights };''')

s = s.replace('''    const hits = Math.min(1, Number(strength[ep.id]?.hits || 0) / 5);
    const score = lex * w.lex + rec * w.recency + sal * w.salience + aff * w.affect + hits * w.hits;''',
'''    const hits = Math.min(1, Number(strength[ep.id]?.hits || 0) / 5);
    // 完全模式：不做时间衰减（recency 权重归零），其余维度保留
    const score = lex * w.lex + (full ? 0 : rec * w.recency) + sal * w.salience + aff * w.affect + hits * w.hits;''')

s = s.replace('''  scored.sort((a, b) => b.score - a.score);
  const top = scored.slice(0, 6);''',
'''  scored.sort((a, b) => b.score - a.score);
  const limit = full ? Math.min(50, scored.length) : 6;
  const top = scored.slice(0, limit);''')

# full 模式不降低强度
s = s.replace('''  touchStrength(top.map((x) => x.id), 0.1);''',
'''  if (!full) touchStrength(top.map((x) => x.id), 0.1);''')

p.write_text(s, encoding="utf-8")
ast.parse("pass")
print("recall patched (python ast parse skipped for mjs)")