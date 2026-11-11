```javascript
import { createServer, IncomingMessage, ServerResponse } from 'node:http';
import { URL } from 'node:url';

export function startHttpServer({ port, handlers }) {
  const server = createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const { pathname } = url;
    const contentType = 'application/json; charset=utf-8';

    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
      });
      res.end();
      return;
    }

    res.setHeader('Access-Control-Allow-Origin', '*');

    if (req.method === 'GET') {
      if (pathname === '/health') {
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(JSON.stringify({ ok: true, service: 'anshiyu-life-core', ts: Date.now() }));
      } else if (pathname === '/state') {
        handlers.getState()
          .then(state => {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(JSON.stringify(state));
          })
          .catch(error => {
            res.writeHead(500, { 'Content-Type': contentType });
            res.end(JSON.stringify({ ok: false, error: error.message }));
          });
      } else if (pathname === '/memories') {
        const limit = parseInt(url.searchParams.get('limit') || '10', 10);
        handlers.getMemories(limit)
          .then(memories => {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(JSON.stringify(memories));
          })
          .catch(error => {
            res.writeHead(500, { 'Content-Type': contentType });
            res.end(JSON.stringify({ ok: false, error: error.message }));
          });
      } else {
        res.writeHead(404, { 'Content-Type': contentType });
        res.end(JSON.stringify({ ok: false, error: 'Not Found' }));
      }
    } else if (req.method === 'POST') {
      if (pathname === '/chat') {
        let body = '';
        req.on('data', chunk => {
          body += chunk.toString();
        });
        req.on('end', () => {
          try {
            const { text } = JSON.parse(body);
            handlers.chat(text)
              .then(response => {
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(JSON.stringify(response));
              })
              .catch(error => {
                res.writeHead(500, { 'Content-Type': contentType });
                res.end(JSON.stringify({ ok: false, error: error.message }));
              });
          } catch (error) {
            res.writeHead(400, { 'Content-Type': contentType });
            res.end(JSON.stringify({ ok: false, error: 'Invalid JSON' }));
          }
        });
      } else if (pathname === '/event') {
        let body = '';
        req.on('data', chunk => {
          body += chunk.toString();
        });
        req.on('end', () => {
          try {
            const payload = JSON.parse(body);
            handlers.event(payload)
              .then(response => {
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(JSON.stringify(response));
              })
              .catch(error => {
                res.writeHead(500, { 'Content-Type': contentType });
                res.end(JSON.stringify({ ok: false, error: error.message }));
              });
          } catch (error) {
            res.writeHead(400, { 'Content-Type': contentType });
            res.end(JSON.stringify({ ok: false, error: 'Invalid JSON' }));
          }
        });
      } else {
        res.writeHead(404, { 'Content-Type': contentType });
        res.end(JSON.stringify({ ok: false, error: 'Not Found' }));
      }
    } else {
      res.writeHead(405, { 'Content-Type': contentType });
      res.end(JSON.stringify({ ok: false, error: 'Method Not Allowed' }));
    }
  });

  server.on('error', (err) => {
    console.error('Server error:', err);
  });

  server.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
  });

  return server;
}
```