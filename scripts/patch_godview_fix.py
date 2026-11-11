from pathlib import Path

# 修前端重复表情前缀
p = Path(r"D:\大肥鱼\anshiyu-server\static\godview.html")
s = p.read_text(encoding="utf-8")
old = """    $('recent').innerHTML = recent.length
      ? recent.map((x) => `<div class="item"><span class="ts">${fmt(x.ts)}</span><span class="emo">（${x.emo || '平静'}）</span>${x.gist || x.text}</div>`).join('')
      : '<div class="empty">暂无</div>';"""
new = """    $('recent').innerHTML = recent.length
      ? recent.map((x) => {
          const g = x.gist || x.text || '';
          const prefix = g.startsWith('（') ? '' : `<span class="emo">（${x.emo || '平静'}）</span>`;
          return `<div class="item"><span class="ts">${fmt(x.ts)}</span>${prefix}${g}</div>`;
        }).join('')
      : '<div class="empty">暂无</div>';"""
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("godview fixed")

# 更新进度
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步（P3-1）
1. 上帝视角前端页（读 /api/godview：状态面板 + 时间轴 + 最近情景 + 意图 + 事实 + 记忆模式开关）
2. B站/抖音分享加入主动消息循环（定时自主刷+分享）
3. 夜间任务结果写日记并同步到动态""",
"""### P3-1 上帝视角前端完成（2026-11-10）
- `anshiyu-server/static/godview.html`：上帝视角页
  - 此刻（地点/活动/心情/记忆模式/情景·事实·意图计数）
  - 24 小时时间轴（当前小时高亮）
  - 最近经历（情景列表）、未完成意图、她记住的事实
  - 记忆模式切换按钮（记忆完全 / 记忆衰减）
  - 每 10 秒自动刷新
- 网关新增 `GET /godview` 路由
- 截图验证通过（`logs/godview.png`）
- 修复：最近经历重复情绪前缀

### 下一步（P3-3）
1. B站/抖音分享加入主动消息循环（定时自主刷+分享）
2. 夜间任务日记同步到她的动态
3. 上帝视角接入鸿蒙 App（Web 组件或原生页）""")
p.write_text(s, encoding="utf-8")
print("progress updated")