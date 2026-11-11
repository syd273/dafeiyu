from pathlib import Path
p = Path(r"D:\大肥鱼\life-core\src\server.mjs")
s = p.read_text(encoding="utf-8")

# 1) 顶部加 fs/path 导入 + feed 路径与写入函数
if "appendPersonaFeed" not in s:
    s = s.replace("import { options, setOptions, memoryMode } from './config.mjs';",
"""import { options, setOptions, memoryMode } from './config.mjs';
import fs from 'node:fs';
import path from 'node:path';

const PERSONA_FEED = path.join('D:', '大肥鱼', 'persona', 'feed.json');

/** 把日记写入她的动态（persona/feed.json），保留最近 60 条 */
function appendPersonaFeed(text, emo = '平静') {
  try {
    let feed = [];
    try {
      feed = JSON.parse(fs.readFileSync(PERSONA_FEED, 'utf8'));
      if (!Array.isArray(feed)) feed = [];
    } catch {
      feed = [];
    }
    feed.unshift({ ts: Date.now(), text: String(text || '').slice(0, 500), emo });
    fs.writeFileSync(PERSONA_FEED, JSON.stringify(feed.slice(0, 60), null, 2), 'utf8');
    return true;
  } catch (e) {
    console.error('[life-core] feed 写入失败:', e?.message || e);
    return false;
  }
}""")

# 2) nightly 成功后写入 feed
    s = s.replace("""    const state = loadState();
    state.lastNightly = { at: Date.now(), processed: cons.processed, diarySource: diary.source };
    saveState(state);
    return { ok: true, consolidate: cons, diary, at: state.lastNightly.at };""",
"""    const state = loadState();
    const feedAdded = diary?.text ? appendPersonaFeed(diary.text, '平静') : false;
    state.lastNightly = { at: Date.now(), processed: cons.processed, diarySource: diary.source, feedAdded };
    saveState(state);
    return { ok: true, consolidate: cons, diary, feedAdded, at: state.lastNightly.at };""")

p.write_text(s, encoding="utf-8")
print("server patched")