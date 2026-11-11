from pathlib import Path
import ast, json

# 1) life_core.add_feed 支持 kind
p = Path(r"D:\大肥鱼\persona\life_core.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''def add_feed(text: str, emo: str = "平静") -> dict:
    feed = load_feed()
    item = {"ts": int(time.time()), "text": text, "emo": emo}''',
'''def add_feed(text: str, emo: str = "平静", kind: str = "talk") -> dict:
    """kind: talk（说说）/ share（分享）/ proactive（主动消息）/ diary（日记）"""
    feed = load_feed()
    item = {"ts": int(time.time()), "text": text, "emo": emo, "kind": kind}''')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("life_core.add_feed kind ok")

# 2) app.py 调用点加 kind
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")
s = s.replace('life_core.add_feed(f"分享了一个B站视频：《{v[\'title\']}》", "开心")',
              'life_core.add_feed(f"分享了一个B站视频：《{v[\'title\']}》", "开心", "share")')
s = s.replace('life_core.add_feed(f"分享了抖音热点：「{h[\'title\']}」", "开心")',
              'life_core.add_feed(f"分享了抖音热点：「{h[\'title\']}」", "开心", "share")')
s = s.replace('life_core.add_feed(f"分享了一个B站视频：《{v[\'title\']}》", "开心")',
              'life_core.add_feed(f"分享了一个B站视频：《{v[\'title\']}》", "开心", "share")')
s = s.replace('life_core.add_feed(f"分享了抖音热点：「{item[\'title\']}」", "开心")',
              'life_core.add_feed(f"分享了抖音热点：「{item[\'title\']}」", "开心", "share")')
s = s.replace('life_core.add_feed(text, "平静")',
              'life_core.add_feed(text, "平静", "proactive")')
p.write_text(s, encoding="utf-8")
ast.parse(s)
print("app.py kind ok")

# 3) Life Core 夜间日记 kind=diary
p = Path(r"D:\大肥鱼\life-core\src\server.mjs")
s = p.read_text(encoding="utf-8")
s = s.replace("function appendPersonaFeed(text, emo = '平静') {",
              "function appendPersonaFeed(text, emo = '平静', kind = 'diary') {")
s = s.replace("feed.unshift({ ts: Date.now(), text: String(text || '').slice(0, 500), emo });",
              "feed.unshift({ ts: Date.now(), text: String(text || '').slice(0, 500), emo, kind });")
s = s.replace("const feedAdded = diary?.text ? appendPersonaFeed(diary.text, '平静') : false;",
              "const feedAdded = diary?.text ? appendPersonaFeed(diary.text, '平静', 'diary') : false;")
p.write_text(s, encoding="utf-8")
print("life-core feed kind ok")