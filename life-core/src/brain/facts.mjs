// 语义记忆（facts）：事实 = 主体 + 谓词 + 客体 + 证据
// 参考 dsh-feiyu brain/facts 的设计（MIT）：无证据不入库、冲突不硬删、谓词闭集
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from '../state.mjs';

const FILE = path.join(DATA_DIR, 'facts.json');

export const PREDICATES = [
  'food.eat', 'activity.do', 'plan.go', 'mood.state',
  'media.like', 'preference.like', 'health.state', 'note',
];

function ensure() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export function allFacts() {
  ensure();
  try {
    return JSON.parse(fs.readFileSync(FILE, 'utf8'));
  } catch {
    return [];
  }
}

function save(items) {
  ensure();
  fs.writeFileSync(FILE, JSON.stringify(items, null, 2), 'utf8');
  return items;
}

/**
 * 写入一条事实。
 * prov（证据 episode id）为空 → 拒绝；同 (s,p,o) → 只加 hits；同 (s,p) 不同 o → disputed
 */
export function addFact({ s = '阿东', p = 'note', o = '', prov = '', ts = Date.now() } = {}) {
  if (!prov || !o) return null;
  if (!PREDICATES.includes(p)) p = 'note';
  const items = allFacts();
  const key = `${s}\u0000${p}\u0000${o}`;
  const hit = items.find((x) => `${x.s}\u0000${x.p}\u0000${x.o}` === key);
  if (hit) {
    hit.hits = Number(hit.hits || 1) + 1;
    hit.updatedAt = ts;
    save(items);
    return hit;
  }
  // 同主体同谓词的不同客体：互相标 disputed
  for (const x of items) {
    if (x.s === s && x.p === p && x.o !== o) {
      x.disputed = true;
      x.updatedAt = ts;
    }
  }
  const row = {
    id: `f_${ts}_${Math.random().toString(36).slice(2, 8)}`,
    s, p, o,
    prov,
    ts,
    hits: 1,
    disputed: false,
  };
  items.push(row);
  save(items);
  return row;
}

export function queryFacts({ p = '', s = '', limit = 50 } = {}) {
  return allFacts()
    .filter((x) => (!p || x.p === p) && (!s || x.s === s))
    .sort((a, b) => b.ts - a.ts)
    .slice(0, limit);
}

/** 规则抽取：从 episode 文本里抽事实（零成本） */
export function ruleFacts(episodes = [], { s = '阿东' } = {}) {
  const rules = [
    { p: 'food.eat', re: /(?:吃|喝)(?:了|过)([^\n，。！？,.!?]{1,18})/ },
    { p: 'activity.do', re: /我(?:在|正在)([^\n，。！？,.!?]{1,24})/ },
    { p: 'plan.go', re: /(?:明天|后天|待会|下午|晚上|周末)(?:要|打算|准备)(?:去|看|做|陪)([^\n，。！？,.!?]{1,24})/ },
    { p: 'mood.state', re: /我(?:有点|很|好|特别|今天)?(累了|累|困|烦|难受|开心|不高兴|无聊)/ },
    { p: 'media.like', re: /《([^》]{1,24})》/ },
    { p: 'health.state', re: /(发烧|过敏|头疼|感冒|失眠|肚子疼)/ },
  ];
  const out = [];
  for (const ep of episodes) {
    const text = String(ep.text || '');
    for (const r of rules) {
      const m = text.match(r.re);
      if (!m) continue;
      const o = String(m[1]).trim();
      if (!o) continue;
      out.push({ s, p: r.p, o, prov: ep.id, ts: ep.ts });
    }
  }
  return out;
}
