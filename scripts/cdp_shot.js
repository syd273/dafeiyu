// 用 CDP 截取页面截图：node cdp_shot.js <ws> <outfile>
const fs = require("fs");
const wsUrl = process.argv[2];
const out = process.argv[3] || "shot.png";
const ws = new WebSocket(wsUrl);
let id = 0;
const pend = new Map();
function send(method, params = {}) {
  return new Promise((res) => { const mid = ++id; pend.set(mid, res); ws.send(JSON.stringify({ id: mid, method, params })); });
}
ws.addEventListener("message", (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
});
ws.addEventListener("open", async () => {
  await send("Page.bringToFront", {});
  await new Promise((r) => setTimeout(r, 1200));
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  if (r.result && r.result.data) {
    fs.writeFileSync(out, Buffer.from(r.result.data, "base64"));
    console.log("saved", out);
  } else {
    console.log("fail", JSON.stringify(r).slice(0, 300));
  }
  process.exit(0);
});
setTimeout(() => process.exit(0), 20000);
