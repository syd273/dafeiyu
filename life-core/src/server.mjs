// 安诗鱼 Life Core · 入口 v0.4（记忆完全模式 + 夜间巩固）
import { startHttpServer } from './http.mjs';
import { loadState, saveState } from './state.mjs';
import { appendEpisode, allEpisodes } from './brain/episode.mjs';
import { recallEpisodes, renderForPrompt } from './brain/recall.mjs';
import { feel, decay, state as affectState, label as affectLabel } from './brain/affect.mjs';
import { writeDiary } from './brain/self.mjs';
import { queryFacts, allFacts } from './brain/facts.mjs';
import { all as allIntents, open as openIntents, extract as extractIntent, done as markDone } from './brain/intents.mjs';
import { consolidate } from './brain/consolidate.mjs';
import { options, setOptions, memoryMode } from './config.mjs';
import fs from 'node:fs';
import path from 'node:path';

const PERSONA_FEED = path.join('D:', '大肥鱼', 'persona', 'feed.json');

/** 把日记写入她的动态（persona/feed.json），保留最近 60 条 */
function appendPersonaFeed(text, emo = '平静', kind = 'diary') {
  try {
    let feed = [];
    try {
      feed = JSON.parse(fs.readFileSync(PERSONA_FEED, 'utf8'));
      if (!Array.isArray(feed)) feed = [];
    } catch {
      feed = [];
    }
    feed.unshift({ ts: Date.now(), text: String(text || '').slice(0, 500), emo, kind });
    fs.writeFileSync(PERSONA_FEED, JSON.stringify(feed.slice(0, 60), null, 2), 'utf8');
    return true;
  } catch (e) {
    console.error('[life-core] feed 写入失败:', e?.message || e);
    return false;
  }
}

const PORT = Number(process.env.LIFE_CORE_PORT || 8910);

// 记忆完全模式：全量情景常驻内存
let episodeCache = null;
function episodes() {
  if (memoryMode() === 'full') {
    if (episodeCache === null) episodeCache = allEpisodes();
    return episodeCache;
  }
  episodeCache = null;
  return allEpisodes();
}

function invalidateCache() {
  episodeCache = null;
}

const handlers = {
  async getState() {
    decay();
    const state = loadState();
    const aff = affectState();
    const opts = options();
    const eps = episodes(); // full 模式下确保缓存已建立
    return {
      ok: true,
      service: 'anshiyu-life-core',
      version: 4,
      memoryMode: opts.memoryMode,
      cached: opts.memoryMode === 'full' ? eps.length : 0,
      mood: { ...aff, label: affectLabel(aff) },
      life: state.life,
      episodes: allEpisodes().length,
      facts: allFacts().length,
      intents: openIntents().length,
      lastEvent: state.lastEvent,
      lastNightly: state.lastNightly || null,
    };
  },

  async getMemories(limit) {
    return {
      ok: true,
      mode: memoryMode(),
      items: episodes().slice(0, limit).map((e) => ({
        id: e.id, ts: e.ts, gist: e.gist, text: e.text, emo: e.emo,
      })),
    };
  },

  async chat(text) {
    const t = String(text || '').trim();
    if (!t) return { ok: false, error: 'empty text' };
    const hits = recallEpisodes(episodes(), { query: t, mode: memoryMode(), halfLifeDays: options().halfLifeDays });
    return {
      ok: true,
      reply: `（life-core v0.4）关于"${t.slice(0, 30)}"，我想起：${renderForPrompt(hits.slice(0, 3)) || '暂时没有'}。`,
      memories: hits.slice(0, 3),
      mode: memoryMode(),
      ts: Date.now(),
    };
  },

  async event(payload) {
    const text = String(payload?.text || payload?.kind || '');
    if (!text) return { ok: false, error: 'empty event' };
    const ep = appendEpisode({
      text,
      kind: String(payload?.kind || 'event'),
      emo: String(payload?.emo || ''),
      ts: Date.now(),
      meta: payload?.meta || {},
    });
    if (episodeCache) episodeCache.unshift(ep);
    const aff = feel({ valence: ep.valence, arousal: ep.emo === '平静' ? 0.3 : 0.6, tension: 0 });
    const intent = extractIntent(ep);
    const state = loadState();
    state.lastEvent = { kind: ep.kind, text: ep.text, ts: ep.ts };
    saveState(state);
    return { ok: true, episode: ep, intent, mood: { ...aff, label: affectLabel(aff) }, memoryMode: memoryMode() };
  },

  async recall(query) {
    const hits = recallEpisodes(episodes(), { query: String(query || ''), mode: memoryMode(), halfLifeDays: options().halfLifeDays });
    return { ok: true, mode: memoryMode(), items: hits, context: renderForPrompt(hits) };
  },

  async diary() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const eps = episodes().filter((e) => e.ts >= today.getTime());
    const result = await writeDiary(eps);
    return { ok: true, ...result, count: eps.length };
  },

  async facts({ p = '', s = '', limit = 50 } = {}) {
    return { ok: true, items: queryFacts({ p, s, limit }) };
  },

  async intents() {
    return { ok: true, items: allIntents() };
  },

  async intentDone(id) {
    const row = markDone(id);
    return row ? { ok: true, intent: row } : { ok: false, error: 'not found' };
  },

  async consolidate(payload = {}) {
    const r = consolidate({ ownerName: String(payload?.ownerName || '阿东') });
    invalidateCache();
    return { ok: true, ...r };
  },

  async getMode() {
    return { ok: true, ...options(), episodes: allEpisodes().length, cached: episodeCache ? episodeCache.length : 0 };
  },

  async getOptions() {
    return { ok: true, ...options() };
  },

  async setOptions(payload = {}) {
    const patched = setOptions({ ...payload });
    if (patched.memoryMode === 'full') episodeCache = allEpisodes();
    return { ok: true, ...patched };
  },

  async setMode(payload = {}) {
    const patched = setOptions({
      memoryMode: payload.memoryMode,
      nightlyHour: payload.nightlyHour,
      nightlyMinute: payload.nightlyMinute,
    });
    invalidateCache();
    if (patched.memoryMode === 'full') episodeCache = allEpisodes();
    return { ok: true, ...patched, episodes: allEpisodes().length, cached: episodeCache ? episodeCache.length : 0 };
  },

  /** 夜间巩固：合并情景→事实/意图 + 生成日记 */
  async nightly(payload = {}) {
    const opts = options();
    const cons = opts.nightlyReflect === false
      ? { processed: 0, skipped: true }
      : consolidate({ ownerName: String(payload?.ownerName || '阿东') });
    invalidateCache();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const eps = allEpisodes().filter((e) => e.ts >= today.getTime());
    const diary = await writeDiary(eps);
    const state = loadState();
    const feedAdded = diary?.text ? appendPersonaFeed(diary.text, '平静', 'diary') : false;
    state.lastNightly = { at: Date.now(), processed: cons.processed, diarySource: diary.source, feedAdded };
    saveState(state);
    return { ok: true, consolidate: cons, diary, feedAdded, at: state.lastNightly.at };
  },
};

startHttpServer({ port: PORT, handlers });

// 夜间定时任务（默认每天 03:30；按 options 配置）
let nightlyTimer = null;
function scheduleNightly() {
  if (nightlyTimer) clearInterval(nightlyTimer);
  nightlyTimer = setInterval(async () => {
    try {
      const o = options();
      const now = new Date();
      const stamp = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
      const state = loadState();
      if (state.lastNightly?.stamp === stamp) return;
      if (now.getHours() !== o.nightlyHour || now.getMinutes() < o.nightlyMinute) return;
      await handlers.nightly({});
      const st = loadState();
      st.lastNightly = { ...(st.lastNightly || {}), stamp };
      saveState(st);
    } catch (e) {
      console.error('[life-core] nightly error:', e?.message || e);
    }
  }, 60 * 1000);
}
scheduleNightly();
