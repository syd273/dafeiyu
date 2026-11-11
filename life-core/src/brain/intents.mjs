// 前瞻记忆（intents）：承诺/打算/愿望
// 参考 dsh-feiyu brain/intents 的三态设计（MIT），简化：open / done / failed
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from '../state.mjs';
import { feel } from './affect.mjs';

const FILE = path.join(DATA_DIR, 'intents.json');
const KINDS = ['intent', 'wish', 'blocked'];

function ensure() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export function all() {
  ensure();
  try {
    return JSON.parse(fs.readFileSync(FILE, 'utf8')).items || [];
  } catch {
    return [];
  }
}

function save(items) {
  ensure();
  fs.writeFileSync(FILE, JSON.stringify({ items, updatedAt: Date.now() }, null, 2), 'utf8');
  return items;
}

/** 从一条 episode 里抽"答应/打算" */
export function extract(episode = {}, { now = Date.now() } = {}) {
  const text = String(episode.text || '');
  const m = text.match(/(答应|说好|一定|保证|明天要|后天要|待会要|等会要|晚上要|下午要|周末要)([^\n，。！？,.!?]{1,40})/);
  if (!m) return null;
  const object = `${m[1]}${m[2]}`.slice(0, 60);
  return addIntent({ object, kind: 'intent', dueAt: now + 24 * 3600 * 1000, cueTs: now, prov: episode.id });
}

/** 建账（去重：同 kind+object 且 10 分钟内） */
export function addIntent({ object = '', kind = 'intent', dueAt = 0, cueTs = Date.now(), prov = '' } = {}) {
  const obj = String(object || '').trim().slice(0, 60);
  if (!obj) return null;
  if (!KINDS.includes(kind)) kind = 'intent';
  const items = all();
  const dup = items.find((x) =>
    x.kind === kind && x.object === obj && Math.abs((x.createdAt || 0) - cueTs) < 10 * 60 * 1000);
  if (dup) return dup;
  const row = {
    id: `i_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    kind, object: obj, prov,
    state: 'open',
    dueAt: dueAt || Date.now() + 90 * 60 * 1000,
    createdAt: Date.now(),
    doneAt: 0,
  };
  items.push(row);
  save(items);
  return row;
}

export function open(now = Date.now()) {
  return all().filter((x) => x.state === 'open');
}

export function due(now = Date.now()) {
  return open(now).filter((x) => x.dueAt && x.dueAt <= now);
}

export function done(id) {
  const items = all();
  const row = items.find((x) => x.id === id);
  if (!row) return null;
  row.state = 'done';
  row.doneAt = Date.now();
  save(items);
  // 兑现给一点正向情绪（多巴胺）
  feel({ valence: 0.2, arousal: 0.5, tension: -0.2 });
  return row;
}

export function fail(id) {
  const items = all();
  const row = items.find((x) => x.id === id);
  if (!row) return null;
  row.state = 'failed';
  row.doneAt = Date.now();
  save(items);
  return row;
}
