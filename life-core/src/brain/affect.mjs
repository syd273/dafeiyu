// 情绪状态（affect）：记忆着色 + 缓慢衰减
// 参考 dsh-feiyu brain/affect 的思路（MIT），简化重写
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from '../state.mjs';

const FILE = path.join(DATA_DIR, 'affect.json');
const EMPTY = { valence: 0, arousal: 0.3, tension: 0, updatedAt: 0 };

function ensure() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export function state() {
  try {
    return { ...EMPTY, ...JSON.parse(fs.readFileSync(FILE, 'utf8')) };
  } catch {
    return { ...EMPTY };
  }
}

function save(s) {
  ensure();
  fs.writeFileSync(FILE, JSON.stringify(s, null, 2), 'utf8');
  return s;
}

/** 体验一次情绪（带惯性，不完全覆盖） */
export function feel({ valence = 0, arousal = 0.3, tension = 0 } = {}) {
  const cur = state();
  const next = {
    valence: clamp(cur.valence * 0.6 + valence * 0.4),
    arousal: clamp(cur.arousal * 0.6 + arousal * 0.4),
    tension: Math.max(0, Math.min(3, cur.tension * 0.8 + tension)),
    updatedAt: Date.now(),
  };
  return save(next);
}

/** 睡眠淡化：随时间回落到平稳 */
export function decay(now = Date.now()) {
  const cur = state();
  const hours = Math.max(0, (now - (cur.updatedAt || now)) / 3600000);
  if (hours < 0.2) return cur;
  const k = Math.exp(-hours / 12); // 12 小时衰减常数
  return save({
    valence: Number((cur.valence * k).toFixed(2)),
    arousal: Number((0.3 + (cur.arousal - 0.3) * k).toFixed(2)),
    tension: Number((cur.tension * k).toFixed(2)),
    updatedAt: now,
  });
}

export function label(s = state()) {
  if (s.tension >= 2 && s.valence <= -0.1) return '心里压着事';
  if (s.valence >= 0.35 && s.arousal >= 0.55) return '雀跃';
  if (s.valence >= 0.15) return '高兴';
  if (s.valence <= -0.35) return '低落';
  if (s.arousal >= 0.65) return '有点上头';
  return '平稳';
}

function clamp(v) {
  return Math.max(-1, Math.min(1, Number(v.toFixed(2))));
}
