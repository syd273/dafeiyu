from pathlib import Path
p = Path(r"D:\大肥鱼\anshiyu-server\static\godview.html")
s = p.read_text(encoding="utf-8")

# 1) 样式：标签与筛选按钮
s = s.replace("""  .full { grid-column:1 / -1; }""",
"""  .full { grid-column:1 / -1; }
  .tag { display:inline-block; font-size:11px; padding:1px 7px; border-radius:999px; margin-right:6px; border:1px solid; }
  .tag.talk { color:#8fa2d8; border-color:#33415f; }
  .tag.share { color:#c39bff; border-color:#5b4a86; }
  .tag.proactive { color:#ffc98a; border-color:#8a6a3d; }
  .tag.diary { color:#9fe0b8; border-color:#3d7a58; }
  .fbtn { padding:3px 9px; font-size:11.5px; border-radius:999px; }""")

# 2) 动态区块加筛选栏
s = s.replace("""  <section class="card full">
    <h2>她的动态</h2>
    <div id="feed"><div class="empty">暂无</div></div>
  </section>""",
"""  <section class="card full">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap">
      <h2 style="margin:0">她的动态</h2>
      <span id="feedFilter">
        <button class="fbtn on" data-f="all">全部</button>
        <button class="fbtn" data-f="talk">说说</button>
        <button class="fbtn" data-f="share">分享</button>
        <button class="fbtn" data-f="proactive">主动</button>
        <button class="fbtn" data-f="diary">日记</button>
      </span>
    </div>
    <div id="feed"><div class="empty">暂无</div></div>
  </section>""")

# 3) JS：feed 数据与筛选渲染
s = s.replace("""function renderTimeline() {""",
"""let feedData = [];
let feedFilter = 'all';
const FEED_LABEL = { talk: '说说', share: '分享', proactive: '主动', diary: '日记' };

function renderFeed() {
  const box = $('feed');
  if (!box) return;
  const items = (feedData || []).filter((x) => feedFilter === 'all' || (x.kind || 'talk') === feedFilter);
  box.innerHTML = items.length
    ? items.slice(0, 8).map((x) => {
        const kind = x.kind || 'talk';
        return `<div class="item"><span class="ts">${fmt(x.ts)}</span>`
          + `<span class="tag ${kind}">${FEED_LABEL[kind] || '说说'}</span>${x.text}</div>`;
      }).join('')
    : '<div class="empty">暂无</div>';
}

function renderTimeline() {""")

s = s.replace("""    try {
      const fr = await fetch(`/api/feed?token=${TOKEN}`);
      const fd = await fr.json();
      const items = fd.items || [];
      $('feed').innerHTML = items.length
        ? items.slice(0, 6).map((x) => `<div class="item"><span class="ts">${fmt(x.ts)}</span>${x.text}</div>`).join('')
        : '<div class="empty">暂无</div>';
    } catch (e) {
      $('feed').innerHTML = '<div class="empty">读取失败</div>';
    }""",
"""    try {
      const fr = await fetch(`/api/feed?token=${TOKEN}`);
      const fd = await fr.json();
      feedData = fd.items || [];
      renderFeed();
    } catch (e) {
      $('feed').innerHTML = '<div class="empty">读取失败</div>';
    }""")

# 4) 筛选按钮事件（在 load() 调用前）
s = s.replace("""$('btnFull').addEventListener('click', () => setMode('full'));""",
"""document.querySelectorAll('#feedFilter .fbtn').forEach((b) => {
  b.addEventListener('click', () => {
    feedFilter = b.dataset.f;
    document.querySelectorAll('#feedFilter .fbtn').forEach((x) => x.classList.toggle('on', x === b));
    renderFeed();
  });
});

$('btnFull').addEventListener('click', () => setMode('full'));""")

p.write_text(s, encoding="utf-8")
print("godview feed kinds added")