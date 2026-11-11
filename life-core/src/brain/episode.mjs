// 情景记忆（episode）：事件 → 一条"事情"，append-only
// 参考 dsh-feiyu brain/episode 的设计（MIT），按 life-core 简化重写
import fs from 'node:fs';
import { options } from '../config.mjs';
import path from 'node:path';
import { DATA_DIR } from '../state.mjs';

const EP_FILE = path.join(DATA_DIR, 'episodes.jsonl');
const STRENGTH_FILE = path.join(DATA_DIR, 'strength.json');

const POS = /开心|高兴|笑死|太好|好耶|喜欢|爱了|爽|舒服|可爱|好听|好看|厉害|谢谢|抱抱|亲亲|哈哈/;
const NEG = /难过|难受|哭|累|烦|气死|生气|崩溃|无聊|害怕|慌|痛|失眠|加班|糟|讨厌|焦虑/;

function ensure() {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

/** 情绪极性：返回 { emo, valence } */
export function feelOf(text = '') {
  const t = String(text);
  if (POS.test(t)) return { emo: '开心', valence: 0.7 };
  if (NEG.test(t)) return { emo: '低落', valence: -0.7 };
  return { emo: '平静', valence: 0 };
}

/** 显著性：长文本、带情绪、有人名/约定 → 更显著 */
export function salienceOf(text = '', emo = '平静') {
  const t = String(text);
  let s = 0.3;
  if (t.length > 30) s += 0.15;
  if (t.length > 80) s += 0.1;
  if (emo !== '平静') s += 0.25;
  if (/答应|约定|记住|重要|第一次|生日/.test(t)) s += 0.15;
  return Math.min(1, Number(s.toFixed(2)));
}

/** 规则 gist：取首句 + 情绪，供快速召回渲染 */
export function gistOf(text = '', emo = '平静') {
  const first = String(text).split(/[。！？\n]/)[0].trim().slice(0, 60);
  return emo === '平静' ? first : `（${emo}）${first}`;
}

/** 追加一条情景（append-only） */
function trimEpisodes() {
  try {
    const max = Number(options().maxEpisodes || 0);
    if (!max) return;
    const rows = allEpisodes(); // 新 -> 旧
    if (rows.length <= max) return;
    const keep = rows.slice(0, max).reverse(); // 旧 -> 新
    fs.writeFileSync(EP_FILE, keep.map((r) => JSON.stringify(r)).join('\n') + '\n', 'utf8');
  } catch (e) { }
}

export function appendEpisode({ text, kind = 'event', emo = '', ts = Date.now(), meta = {} }) {
  ensure();
  const t = String(text || '').slice(0, 2000);
  const felt = feelOf(t);
  const finalEmo = emo || felt.emo;
  const row = {
    id: `ep_${ts}_${Math.random().toString(36).slice(2, 8)}`,
    ts,
    kind,
    text: t,
    gist: gistOf(t, finalEmo),
    emo: finalEmo,
    valence: felt.valence,
    salience: salienceOf(t, finalEmo),
    meta,
  };
  fs.appendFileSync(EP_FILE, JSON.stringify(row) + '\n', 'utf8');
  trimEpisodes();
  return row;
}

/** 读取全部情景（倒序，新→旧） */
export function allEpisodes() {
  ensure();
  try {
    const lines = fs.readFileSync(EP_FILE, 'utf8').split('\n').filter(Boolean);
    return lines.map((l) => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean).reverse();
  } catch {
    return [];
  }
}

/** 强度表（被召回次数越多越强） */
export function strengths() {
  ensure();
  try {
    return JSON.parse(fs.readFileSync(STRENGTH_FILE, 'utf8'));
  } catch {
    return {};
  }
}

export function touchStrength(ids = [], delta = 0.2) {
  const list = Array.isArray(ids) ? ids : [ids];
  if (!list.length) return;
  const cur = strengths();
  for (const id of list) {
    const row = cur[id] || { strength: 1, hits: 0 };
    row.hits += 1;
    row.strength = Math.min(3, Number((row.strength + delta).toFixed(2)));
    cur[id] = row;
  }
  ensure();
  fs.writeFileSync(STRENGTH_FILE, JSON.stringify(cur, null, 2), 'utf8');
}
