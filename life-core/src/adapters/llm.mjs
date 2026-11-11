// LLM 适配器：直连 OpenAI 兼容接口（用户自填 Key）
// 生产要求：配置写在 data/config.json（api_key/base_url/model），不提交到仓库
// 测试可用 LIFE_CORE_NO_LLM=1 强制跳过
import fs from 'node:fs';
import path from 'node:path';
import { DATA_DIR } from '../state.mjs';

const CFG_FILE = path.join(DATA_DIR, 'config.json');

function loadCfg() {
  try {
    return JSON.parse(fs.readFileSync(CFG_FILE, 'utf8'));
  } catch {
    return {};
  }
}

/** 依次取：环境变量 → data/config.json →（仅本地开发）D:\大肥鱼\deepseek-key.txt */
export function apiConfig() {
  const cfg = loadCfg();
  const base = process.env.LLM_BASE_URL || cfg.base_url || 'https://api.deepseek.com/v1';
  const model = process.env.LLM_MODEL || cfg.model || 'deepseek-chat';
  let key = process.env.LLM_API_KEY || cfg.api_key || '';
  if (!key) {
    try {
      key = fs.readFileSync(path.join('D:', '大肥鱼', 'deepseek-key.txt'), 'utf8').trim();
    } catch {
      key = '';
    }
  }
  return { base: base.replace(/\/+$/, ''), model, key };
}

/** 调用一次对话；失败返回 null（调用方兜底） */
export async function chat(messages, { maxTokens = 500, temperature = 0.8, timeoutMs = 60000 } = {}) {
  if (process.env.LIFE_CORE_NO_LLM === '1') return null;
  const { base, model, key } = apiConfig();
  if (!key) return null;
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    const res = await fetch(`${base}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
      body: JSON.stringify({ model, messages, temperature, max_tokens: maxTokens }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (!res.ok) return null;
    const data = await res.json();
    return data?.choices?.[0]?.message?.content?.trim() || null;
  } catch {
    return null;
  }
}
