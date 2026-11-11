# -*- coding: utf-8 -*-
import base64
import os
import re

import requests

s = open(r"D:\大肥鱼\milky-way-3d\lib\three.module.min.js", encoding="utf-8", errors="ignore").read(300000)
m = re.search(r"REVISION\s*=\s*[\"']?(\d+)", s)
print("three REVISION:", m.group(1) if m else "未知")
ver = m.group(1) if m else "160"


def dl(path: str, out: str) -> bool:
    url = f"https://api.github.com/repos/mrdoob/three.js/contents/{path}?ref=r{ver}"
    r = requests.get(url, headers={"User-Agent": "anshiyu"}, timeout=40,
                     proxies={"http": None, "https": None})
    if r.status_code != 200:
        print("下载失败", path, r.status_code)
        return False
    data = base64.b64decode(r.json()["content"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(data)
    print("ok", path, len(data))
    return True


dl("examples/jsm/loaders/GLTFLoader.js", r"D:\大肥鱼\milky-way-3d\lib\GLTFLoader.js")
dl("examples/jsm/utils/BufferGeometryUtils.js", r"D:\大肥鱼\milky-way-3d\lib\BufferGeometryUtils.js")
