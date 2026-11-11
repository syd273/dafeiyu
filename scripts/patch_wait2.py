from pathlib import Path
import re
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
old = """    const el = document.getElementById('life-status');
    if (el) {
      const p = st.silent ? '（在休息）' : '';
      el.innerHTML = `${st.location} · ${st.activity}${p}` +
        (st.event ? `<br><span style="color:#8fa2d8">${st.event}</span>` : '');
    }"""
new = """    const el = document.getElementById('life-status');
    if (el) {
      if (st.waiting) {
        el.innerHTML = '<span style="color:#8fa2d8">她还没醒 · 等你跟她说第一句话</span>';
      } else {
        const p = st.silent ? '（在休息）' : '';
        el.innerHTML = `${st.location} · ${st.activity}${p}` +
          (st.event ? `<br><span style="color:#8fa2d8">${st.event}</span>` : '');
      }
    }"""
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("frontend patched")
else:
    # 退化为逐行插入
    lines = s.splitlines()
    out, inserted = [], False
    for i, ln in enumerate(lines):
        if (not inserted) and "const el = document.getElementById('life-status');" in ln:
            out.append(ln)
            out.append("    if (el && st.waiting) { el.innerHTML = '<span style=\"color:#8fa2d8\">她还没醒 · 等你跟她说第一句话</span>'; }")
            out.append("    else if (el) {")
            inserted = True
            continue
        out.append(ln)
    s = "\n".join(out)
    # 把原 if(el){ ... } 改成 else 分支：简单处理——保留原块，但在其前跳过重复判断
    p.write_text(s, encoding="utf-8")
    print("fallback inserted")