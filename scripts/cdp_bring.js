// 激活指定标签页到最前
const wsUrl = process.argv[2];
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
  await send("Emulation.setFocusEmulationEnabled", { enabled: true }).catch(() => {});
  const r = await send("Runtime.evaluate", { expression: "location.reload(); 'activated'", returnByValue: true });
  console.log(JSON.stringify(r.result && r.result.result && r.result.result.value));
  setTimeout(() => process.exit(0), 1500);
});
setTimeout(() => process.exit(0), 10000);
