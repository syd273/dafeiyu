// 检索回路（recall）：多路召回 → 加权排序 → 渲染
// 参考 dsh-feiyu brain/recall 的权重设计（MIT），按 life-core 简化重写
import { strengths, touchStrength } from './episode.mjs';

export const DEFAULT_WEIGHTS = {
  lex: 0.42,      // 字面/关键词匹配
  recency: 0.14,  // 时间衰减
  salience: 0.20, // 显著性
  affect: 0.18,   // 情绪强度
  hits: 0.06,     // 被召回次数
};

const HALF_LIFE_MS = 26 * 3600 * 1000; // 26 小时半衰期
const STOP = new Set(['的', '是', '在', '和', '有', '我', '你', '他', '她', '它', '了', '就', '都', '也', '不', '吗', '呢', '啊', '吧', '这', '那', '什么', '怎么']);

/** 中文 2-gram + 英文/数字整词 */
export function grams(text = '') {
  const t = String(text).toLowerCase();
  const out = new Set();
  const words = t.match(/[a-z0-9_]{2,}/g) || [];
  for (const w of words) out.add(w);
  const zh = t.replace(/[^\u4e00-\u9fa5]/g, '');
  for (let i = 0; i < zh.length - 1; i++) {
    const g = zh.slice(i, i + 2);
    if (!STOP.has(g)) out.add(g);
  }
  return out;
}

function lexScore(qGrams, text) {
  if (!qGrams.size) return 0;
  const tGrams = grams(text);
  let hit = 0;
  for (const g of qGrams) if (tGrams.has(g)) hit++;
  return hit / qGrams.size;
}

function recencyScore(ts, now, halfLifeMs = HALF_LIFE_MS) {
  const dt = Math.max(0, now - Number(ts || 0));
  return Math.exp(-dt / Math.max(1, halfLifeMs));
}

/** 主函数：返回最多 6 条带 score 的记忆 */
export function recallEpisodes(episodes = [], { query = '', now = Date.now(), weights = {}, mode = 'decay', halfLifeDays = 0 } = {}) {
  const halfLifeMs = halfLifeDays > 0 ? halfLifeDays * 86400000 : HALF_LIFE_MS;
  const full = mode === 'full';
  const w = { ...DEFAULT_WEIGHTS, ...(full ? { recency: 0 } : {}), ...weights };
  const sum = Object.values(w).reduce((a, b) => a + Number(b || 0), 0) || 1;
  for (const k of Object.keys(w)) w[k] = Number(w[k] || 0) / sum;

  const qGrams = grams(query);
  const strength = strengths();

  const scored = episodes.map((ep) => {
    const lex = lexScore(qGrams, `${ep.text || ''} ${ep.gist || ''}`);
    const rec = recencyScore(ep.ts, now, halfLifeMs);
    const sal = Number(ep.salience || 0.3);
    const aff = Math.abs(Number(ep.valence || 0));
    const hits = Math.min(1, Number(strength[ep.id]?.hits || 0) / 5);
    // 完全模式：不做时间衰减（recency 权重归零），其余维度保留
    const score = lex * w.lex + (full ? 0 : rec * w.recency) + sal * w.salience + aff * w.affect + hits * w.hits;
    return { ...ep, score: Number(score.toFixed(3)), strength: strength[ep.id]?.strength || 1 };
  });

  scored.sort((a, b) => b.score - a.score);
  const limit = full ? Math.min(50, scored.length) : 6;
  const top = scored.slice(0, limit);
  if (!full) touchStrength(top.map((x) => x.id), 0.1);
  return top;
}

/** 给 LLM 的上下文渲染 */
export function renderForPrompt(items = []) {
  return items.map((x) => `- [${new Date(x.ts).toLocaleString('zh-CN')}] ${x.gist || x.text}`).join('\n');
}
