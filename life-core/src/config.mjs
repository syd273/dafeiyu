// 运行选项（options.json）
// memoryMode: "decay"（默认，艾宾浩斯衰减）| "full"（记忆完全模式：不衰减、全量保留、全量召回）
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from './state.mjs';

const FILE = path.join(DATA_DIR, 'options.json');
const DEFAULTS = {
  memoryMode: 'decay',
  nightlyHour: 3,
  nightlyMinute: 30,
  halfLifeDays: 1.08,   // 记忆半衰期（天）
  maxEpisodes: 0,       // 最多保留情景数（0 = 不限）
  nightlyReflect: true, // 夜间是否巩固/反思
};

function ensure() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

export function options() {
  ensure();
  try {
    return { ...DEFAULTS, ...JSON.parse(fs.readFileSync(FILE, 'utf8')) };
  } catch {
    return { ...DEFAULTS };
  }
}

export function setOptions(patch = {}) {
  const next = { ...options(), ...patch };
  if (!['decay', 'full'].includes(next.memoryMode)) next.memoryMode = 'decay';
  next.halfLifeDays = Math.min(30, Math.max(0.1, Number(next.halfLifeDays) || 1.08));
  next.maxEpisodes = Math.max(0, Number(next.maxEpisodes) || 0);
  ensure();
  fs.writeFileSync(FILE, JSON.stringify(next, null, 2), 'utf8');
  return next;
}

export function memoryMode() {
  return options().memoryMode;
}
