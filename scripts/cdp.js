// CDP 工具：新建页面 / 执行 JS / 模拟键盘输入
// 用法: node cdp.js new <url>
//       node cdp.js eval <wsUrl> <expression>
//       node cdp.js type <wsUrl> <text>
//       node cdp.js key <wsUrl> <key>   (Enter/Tab/Escape/Backspace)
//       node cdp.js click <wsUrl> <selector>
//       node cdp.js paste <wsUrl> <text>   (聚焦后逐字输入)

const http = require("http");

function httpGet(path) {
  return new Promise((resolve, reject) => {
    http.get({ host: "127.0.0.1", port: 9222, path }, (res) => {
      let d = "";
      res.on("data", (c) => (d += c));
      res.on("end", () => resolve(d));
    }).on("error", reject);
  });
}

function httpPut(path) {
  return new Promise((resolve, reject) => {
    const req = http.request({ host: "127.0.0.1", port: 9222, path, method: "PUT" }, (res) => {
      let d = "";
      res.on("data", (c) => (d += c));
      res.on("end", () => resolve(d));
    });
    req.on("error", reject);
    req.end();
  });
}

class CDP {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.id = 0;
    this.pending = new Map();
    this.ready = new Promise((resolve) => {
      this.ws.addEventListener("open", () => resolve());
    });
    this.ws.addEventListener("message", (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && this.pending.has(m.id)) {
        this.pending.get(m.id)(m);
        this.pending.delete(m.id);
      }
    });
  }
  async send(method, params = {}) {
    await this.ready;
    const id = ++this.id;
    return new Promise((resolve) => {
      this.pending.set(id, resolve);
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  async eval(expression) {
    const r = await this.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    return r.result && r.result.result ? r.result.result.value : undefined;
  }
  async key(key, code, text) {
    await this.send("Input.dispatchKeyEvent", {
      type: "keyDown", key, code, text: text || key,
      windowsVirtualKeyCode: key === "Enter" ? 13 : key === "Tab" ? 9 : key === "Backspace" ? 8 : 0,
    });
    await this.send("Input.dispatchKeyEvent", { type: "keyUp", key, code });
  }
  async typeText(text) {
    for (const ch of text) {
      await this.send("Input.dispatchKeyEvent", { type: "char", text: ch });
    }
  }
  close() {
    try { this.ws.close(); } catch (e) {}
  }
}

(async () => {
  const [cmd, ...rest] = process.argv.slice(2);
  if (cmd === "new") {
    const r = await httpPut("/json/new?" + encodeURIComponent(rest[0]));
    console.log(r);
  } else if (cmd === "targets") {
    const list = JSON.parse(await httpGet("/json/list"));
    list.filter((t) => t.type === "page").forEach((t) => console.log(t.webSocketDebuggerUrl + " | " + t.title + " | " + t.url));
  } else if (cmd === "eval") {
    const c = new CDP(rest[0]);
    console.log(JSON.stringify(await c.eval(rest.slice(1).join(" "))));
    c.close();
  } else if (cmd === "type") {
    const c = new CDP(rest[0]);
    await c.eval("window.focus && window.focus()");
    await c.typeText(rest.slice(1).join(" "));
    c.close();
  } else if (cmd === "key") {
    const c = new CDP(rest[0]);
    await c.key(rest[1], rest[1]);
    c.close();
  } else if (cmd === "click") {
    const c = new CDP(rest[0]);
    await c.eval(`document.querySelector(${JSON.stringify(rest[1])})?.click()`);
    c.close();
  } else if (cmd === "clicktext") {
    const c = new CDP(rest[0]);
    await c.eval(`(() => {
      const txt = ${JSON.stringify(rest[1])};
      const els = [...document.querySelectorAll('button,a,div,span,li')];
      const el = els.find(e => (e.innerText||'').trim() === txt) || els.find(e => (e.innerText||'').includes(txt));
      if (el) { el.click(); return 'clicked:' + txt; }
      return 'notfound:' + txt;
    })()`);
    c.close();
  } else {
    console.log("usage: node cdp.js new|targets|eval|type|key|click|clicktext ...");
  }
  process.exit(0);
})();
