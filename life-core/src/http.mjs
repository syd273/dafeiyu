// 安诗鱼 Life Core · HTTP 层（只监听 127.0.0.1，请求体上限 1MB）
import { createServer } from 'node:http';
import { URL } from 'node:url';

const JSON_TYPE = 'application/json; charset=utf-8';
const MAX_BODY = 1024 * 1024;

function send(res, code, obj) {
  const data = JSON.stringify(obj);
  res.writeHead(code, { 'Content-Type': JSON_TYPE, 'Content-Length': Buffer.byteLength(data) });
  res.end(data);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > MAX_BODY) { reject(new Error('body too large')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', () => {
      try {
        const text = Buffer.concat(chunks).toString('utf8');
        resolve(text ? JSON.parse(text) : {});
      } catch {
        reject(new Error('invalid json'));
      }
    });
    req.on('error', reject);
  });
}

export function startHttpServer({ port, host = '127.0.0.1', handlers }) {
  const server = createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Token');

    if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

    let url;
    try {
      url = new URL(req.url, `http://${req.headers.host || '127.0.0.1'}`);
    } catch {
      return send(res, 400, { ok: false, error: 'bad url' });
    }

    try {
      if (req.method === 'GET') {
        const p = url.pathname;
        if (p === '/health') return send(res, 200, { ok: true, service: 'anshiyu-life-core', ts: Date.now() });
        if (p === '/state') return send(res, 200, await handlers.getState());
        if (p === '/memories') {
          const limit = Math.min(200, Math.max(1, parseInt(url.searchParams.get('limit') || '10', 10) || 10));
          return send(res, 200, await handlers.getMemories(limit));
        }
        if (p === '/recall') return send(res, 200, await handlers.recall(url.searchParams.get('q') || ''));
        if (p === '/diary') return send(res, 200, await handlers.diary());
        if (p === '/facts') {
          return send(res, 200, await handlers.facts({
            p: url.searchParams.get('p') || '',
            s: url.searchParams.get('s') || '',
            limit: parseInt(url.searchParams.get('limit') || '50', 10) || 50,
          }));
        }
        if (p === '/intents') return send(res, 200, await handlers.intents());
        if (p === '/mode') return send(res, 200, await handlers.getMode());
  if (p === '/options') return send(res, 200, await handlers.getOptions());
        return send(res, 404, { ok: false, error: 'Not Found' });
      }

      if (req.method === 'POST') {
        const body = await readBody(req);
        const p = url.pathname;
        if (p === '/chat') return send(res, 200, await handlers.chat(String(body.text || '')));
        if (p === '/event') return send(res, 200, await handlers.event(body));
        if (p === '/consolidate') return send(res, 200, await handlers.consolidate(body));
        if (p === '/intent/done') return send(res, 200, await handlers.intentDone(String(body.id || '')));
        if (p === '/mode') return send(res, 200, await handlers.setMode(body));
  if (p === '/options') return send(res, 200, await handlers.setOptions(body));
        if (p === '/nightly/run') return send(res, 200, await handlers.nightly(body));
        return send(res, 404, { ok: false, error: 'Not Found' });
      }

      return send(res, 405, { ok: false, error: 'Method Not Allowed' });
    } catch (err) {
      return send(res, 500, { ok: false, error: String(err?.message || err) });
    }
  });

  server.on('error', (err) => console.error('[life-core] server error:', err));
  server.listen(port, host, () => console.log(`[life-core] listening on http://${host}:${port}`));
  return server;
}
