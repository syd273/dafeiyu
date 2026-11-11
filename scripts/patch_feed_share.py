from pathlib import Path
import ast

# 1) 网关：分享后写入 feed
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

s = s.replace('''            if life_bridge is not None:
                life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
            item = v''',
'''            if life_bridge is not None:
                life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
            try:
                life_core.add_feed(f"分享了一个B站视频：《{v['title']}》", "开心")
            except Exception:
                pass
            item = v''')

s = s.replace('''            if life_bridge is not None:
                life_bridge.event("share", f"在抖音刷到热点「{h['title']}」并分享了", "开心")
            item = h''',
'''            if life_bridge is not None:
                life_bridge.event("share", f"在抖音刷到热点「{h['title']}」并分享了", "开心")
            try:
                life_core.add_feed(f"分享了抖音热点：「{h['title']}」", "开心")
            except Exception:
                pass
            item = h''')

# 分享路由（手动）也写 feed
s = s.replace('''    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")''',
'''    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在B站刷到《{v['title']}》并分享了", "开心")
    try:
        life_core.add_feed(f"分享了一个B站视频：《{v['title']}》", "开心")
    except Exception:
        pass''')
s = s.replace('''    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在抖音刷到热点「{item['title']}」并分享了", "开心")''',
'''    if life_bridge is not None:
        life_res = life_bridge.event("share", f"在抖音刷到热点「{item['title']}」并分享了", "开心")
    try:
        life_core.add_feed(f"分享了抖音热点：「{item['title']}」", "开心")
    except Exception:
        pass''')

p.write_text(s, encoding="utf-8")
ast.parse(s)
print("gateway feed hooks added")

# 2) 上帝视角页增加动态区块
p = Path(r"D:\大肥鱼\anshiyu-server\static\godview.html")
s = p.read_text(encoding="utf-8")
if "她的动态" not in s:
    s = s.replace('''  <section class="card">
    <h2>她记住的事实</h2>
    <div id="facts"><div class="empty">暂无</div></div>
  </section>''',
'''  <section class="card">
    <h2>她记住的事实</h2>
    <div id="facts"><div class="empty">暂无</div></div>
  </section>

  <section class="card full">
    <h2>她的动态</h2>
    <div id="feed"><div class="empty">暂无</div></div>
  </section>''')
    s = s.replace('''    $('status').textContent = `${life.location || ''} ${life.activity || ''} · 上次事件：${lc.lastEvent ? fmt(lc.lastEvent.ts) : '无'}`;''',
'''    try {
      const fr = await fetch(`/api/feed?token=${TOKEN}`);
      const fd = await fr.json();
      const items = fd.items || [];
      $('feed').innerHTML = items.length
        ? items.slice(0, 6).map((x) => `<div class="item"><span class="ts">${fmt(x.ts)}</span>${x.text}</div>`).join('')
        : '<div class="empty">暂无</div>';
    } catch (e) {
      $('feed').innerHTML = '<div class="empty">读取失败</div>';
    }

    $('status').textContent = `${life.location || ''} ${life.activity || ''} · 上次事件：${lc.lastEvent ? fmt(lc.lastEvent.ts) : '无'}`;''')
    p.write_text(s, encoding="utf-8")
    print("godview feed block added")