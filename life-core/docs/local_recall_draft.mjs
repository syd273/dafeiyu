```javascript
import { strict as assert } from 'assert';

// 停用词列表
const STOP_WORDS = new Set(['的', '是', '在', '和', '有', '一个', '不', '我', '你', '他', '她', '它']);

// 计算关键词匹配分数
function lexScore(query, text) {
  const queryWords = query.split('').filter(char => char !== ' ');
  const textWords = text.split('').filter(char => char !== ' ');
  const queryNgrams = queryWords.map((word, i) => word + (textWords[i + 1] || ''));
  const textNgrams = textWords.map((word, i) => word + (textWords[i + 1] || ''));
  const commonNgrams = queryNgrams.filter(ngram => textNgrams.includes(ngram));
  return commonNgrams.length / Math.max(queryNgrams.length, textNgrams.length);
}

// 计算时间衰减分数
function recencyScore(ts, now) {
  const halfLife = 26 * 60 * 60 * 1000; // 26小时
  const timeDiff = now - ts;
  return Math.exp(-timeDiff / halfLife);
}

// 计算综合分数
function calculateScore(episode, query, now, weights) {
  const { lex, recency, salience, affect, hits } = weights;
  const lexScoreVal = lex * lexScore(query, episode.text);
  const recencyScoreVal = recency * recencyScore(episode.ts, now);
  const salienceScoreVal = salience * episode.salience;
  const affectScoreVal = affect * episode.emo;
  const hitsScoreVal = hits * episode.hits;
  return lexScoreVal + recencyScoreVal + salienceScoreVal + affectScoreVal + hitsScoreVal;
}

// 主函数
export function recallEpisodes(episodes, { query, now, weights = { lex: 0.42, recency: 0.14, salience: 0.20, affect: 0.18, hits: 0.06 } }) {
  return episodes
    .map(episode => ({ ...episode, score: calculateScore(episode, query, now, weights) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 6);
}

// 测试用例
const episodes = [
  { id: 1, ts: Date.now() - 1000 * 60 * 60 * 24, text: '今天天气真好', gist: '天气', emo: 0.8, salience: 0.9, strength: 0.7, hits: 2 },
  { id: 2, ts: Date.now() - 1000 * 60 * 60 * 2, text: '我今天去公园', gist: '公园', emo: 0.6, salience: 0.8, strength: 0.6, hits: 1 },
  { id: 3, ts: Date.now() - 1000 * 60 * 60 * 24 * 2, text: '天气预报说明天会下雨', gist: '天气预报', emo: 0.5, salience: 0.7, strength: 0.5, hits: 0 }
];

const now = Date.now();
const result = recallEpisodes(episodes, { query: '天气', now });
console.log(result);
```