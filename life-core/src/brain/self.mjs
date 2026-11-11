// 自我/反思（self）：用今天的经历生成一篇中文日记
// 有 LLM Key 时调用模型；失败/无 Key 时用模板兜底（保证离线也能跑）
import { chat } from '../adapters/llm.mjs';
import { state as affectState, label as affectLabel } from './affect.mjs';

const SYSTEM = `你是安诗鱼，一个住在电脑里、有自己生活的女孩。
用第一人称写一段今天的日记，1-3 句，口语、具体，带一点当时的情绪。
不要写成总结报告，不要用"今天过得真充实"这类套话。只输出日记正文。`;

export async function writeDiary(episodes = [], { ownerName = '' } = {}) {
  const mood = affectLabel(affectState());
  const lines = episodes.slice(0, 8).map((e) => `- ${e.gist || e.text}`).join('\n');
  const prompt = `今天的经历（从新到旧）：\n${lines || '（今天没发生什么特别的事）'}\n\n当前心情：${mood}。` +
    (ownerName ? `\n称呼对方：${ownerName}。` : '') + '\n\n写今天的日记：';

  const text = await chat([
    { role: 'system', content: SYSTEM },
    { role: 'user', content: prompt },
  ], { maxTokens: 220, temperature: 0.9 });

  if (text) return { ok: true, source: 'llm', text };

  // 模板兜底
  const first = episodes[0]?.gist || '今天没发生什么特别的事';
  const fallback = episodes.length
    ? `今天${first}。${mood === '平稳' ? '就这样过去了。' : `心里有点${mood}。`}`
    : '今天很安静，什么都没发生，也挺好。';
  return { ok: true, source: 'template', text: fallback };
}
