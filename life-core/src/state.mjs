// 安诗鱼 Life Core · 状态与持久化（最小版）
// 数据只写 D:\大肥鱼\life-core\data
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.join(HERE, '..');
export const DATA_DIR = path.join(ROOT, 'data');
export const STATE_FILE = path.join(DATA_DIR, 'state.json');

const DEFAULT_STATE = {
  version: 1,
  createdAt: Date.now(),
  mood: { mood: '平静', score: 0.5, updatedAt: 0 },
  life: { location: '家 · 卧室', activity: '发呆', silent: false },
  memories: [],
  lastEvent: null,
};

function ensureDir() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export function loadState() {
  ensureDir();
  try {
    const raw = fs.readFileSync(STATE_FILE, 'utf8');
    return { ...structuredClone(DEFAULT_STATE), ...JSON.parse(raw) };
  } catch {
    return structuredClone(DEFAULT_STATE);
  }
}

export function saveState(state) {
  ensureDir();
  const tmp = STATE_FILE + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(state, null, 2), 'utf8');
  fs.renameSync(tmp, STATE_FILE);
  return state;
}

export function addMemory(text, meta = {}) {
  const state = loadState();
  const item = {
    id: `m_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    text: String(text || '').slice(0, 2000),
    ts: Date.now(),
    kind: meta.kind || 'event',
    emo: meta.emo || '平静',
  };
  state.memories.unshift(item);
  state.memories = state.memories.slice(0, 500);
  saveState(state);
  return item;
}

export function getMemories(limit = 10) {
  const state = loadState();
  return state.memories.slice(0, limit);
}
