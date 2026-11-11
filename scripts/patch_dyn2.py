from pathlib import Path
import ast, re

# 1) sync：只在有新消息时应用一次
p = Path(r"D:\大肥鱼\scripts\sync_memories.py")
s = p.read_text(encoding="utf-8")
s = s.replace('        last_user = cc.execute("SELECT text FROM messages WHERE role=\'user\' ORDER BY id DESC LIMIT 1").fetchone()',
              '        last_user = cc.execute("SELECT text, ts FROM messages WHERE role=\'user\' ORDER BY id DESC LIMIT 1").fetchone()')
s = s.replace('''        if last_user and last_user[0] and life_core is not None:
            life_core.apply_message(last_user[0])
            life_core.mood_drift()''',
'''        if last_user and last_user[0] and life_core is not None:
            stl = life_core.load_state()
            if stl.get("last_applied_msg_ts") != last_user[1]:
                life_core.apply_message(last_user[0])
                stl = life_core.load_state()
                stl["last_applied_msg_ts"] = last_user[1]
                life_core.save_state(stl)
            life_core.mood_drift()''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("sync dedupe ok")

# 2) 前端：动态段样式
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
s = s.replace("const col = TL_COLORS[s.activity] || '#57678f';",
              "const col = s.dynamic ? '#b07cff' : (TL_COLORS[s.activity] || '#57678f');")
s = s.replace("seg.title = `${s.from}:00-${s.to}:00 ${s.location} · ${s.activity}`;",
              "seg.title = `${s.from}:00-${s.to}:00 ${s.location} · ${s.activity}` + (s.reason ? `（${s.reason}）` : '');")
s = s.replace("legend.innerHTML += `<div><span style=\"display:inline-block;width:9px;height:9px;border-radius:2px;background:${col};margin-right:6px\"></span>${s.from}–${s.to} ${s.activity}</div>`;",
              "legend.innerHTML += `<div><span style=\"display:inline-block;width:9px;height:9px;border-radius:2px;background:${col};margin-right:6px\"></span>${s.from}–${s.to} ${s.activity}` + (s.reason ? `<span style=\"color:#8f7ac0\">（${s.reason}）</span>` : '') + `</div>`;")
p.write_text(s, encoding="utf-8")
print("frontend dynamic ok")