// 巩固回路（consolidate）：把新情景 → 事实/意图，幂等可续跑
// 参考 dsh-feiyu brain/consolidate（MIT），简化：done.jsonl 记录已处理 id
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from '../state.mjs';
import { allEpisodes } from './episode.mjs';
import { ruleFacts, addFact } from './facts.mjs';
import { extract as extractIntent } from './intents.mjs';

const DONE_FILE = path.join(DATA_DIR, 'consolidated.jsonl');

function doneIds() {
  try {
    return new Set(
      fs.readFileSync(DONE_FILE, 'utf8').split('\n').filter(Boolean)
        .map((l) => { try { return JSON.parse(l).id; } catch { return null; } })
        .filter(Boolean),
    );
  } catch {
    return new Set();
  }
}

function appendDone(id) {
  fs.appendFileSync(DONE_FILE, JSON.stringify({ id, ts: Date.now() }) + '\n', 'utf8');
}

/**
 * 处理所有未巩固的情景：抽事实 + 抽意图。
 * 返回 { processed, factsAdded, intentsAdded }
 */
export function consolidate({ ownerName = '阿东' } = {}) {
  const done = doneIds();
  const pending = allEpisodes().filter((e) => !done.has(e.id));
  if (!pending.length) return { processed: 0, factsAdded: 0, intentsAdded: 0 };

  const facts = ruleFacts(pending, { s: ownerName });
  let factsAdded = 0;
  for (const f of facts) {
    const row = addFact(f);
    if (row) factsAdded++;
  }

  let intentsAdded = 0;
  for (const ep of pending) {
    const row = extractIntent(ep);
    if (row) intentsAdded++;
  }

  for (const ep of pending) appendDone(ep.id);
  return { processed: pending.length, factsAdded, intentsAdded, facts };
}
