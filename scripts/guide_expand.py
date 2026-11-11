from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Guide.ets")
s = p.read_text(encoding="utf-8")

# 追加插件与修复章节
s = s.replace("""    {
      title: '常见问题',
      body: '离线：点顶栏「重连」，检查是否同一网络\\nIP 变了：App 会自动扫热点网段\\n收不到通知：App 活着时能收，杀掉后打开会补消息\\n额度不足：去 DeepSeek 平台充值\\n备份在哪：D:\\\\大肥鱼\\\\backups\\\\'
    },""",
"""    {
      title: '插件：她的房间（可选）',
      body: '从 GitHub 下载等距房间模型（.gltf，如 Aubrey-Li/cozy-room，MIT）\\n重命名为 room.gltf\\n放到 D:\\\\大肥鱼\\\\milky-way-3d\\\\room\\\\room.gltf\\n打开上帝视角自动加载。\\n不装：页面提示未安装，其他功能正常。\\n关闭：设置 → 功能开关 → 房间展示。'
    },
    {
      title: '插件：表情包（可选）',
      body: '下载 dsh-meme（MIT）的图片放到 persona/stickers/\\n在 persona/stickers.json 登记 id/文字/文件名\\n重启网关生效。\\n不装：她不发表情。\\n关闭：设置 → 功能开关 → 表情包。'
    },
    {
      title: '插件：星图 / 记忆模式 / 服务器',
      body: '星图：内置，可替换 milky-way-3d 下的页面\\n记忆模式：设置里切换（衰减/完全）\\n服务器：本地/云端两套独立配置，接口一致'
    },
    {
      title: '故障修复（常见）',
      body: '离线：点顶栏「重连」；检查同一网络；IP 变了 App 会自动扫\\n测试连接失败：服务没起/防火墙，重跑 start_all.ps1\\n测试 Key 失败：Key 错/余额不足，去平台看余额\\n端口被占：Get-NetTCPConnection -LocalPort 8900 → Stop-Process -Id PID -Force\\n服务起不来：装 Python 3.12 + Node 20+，重跑 setup.ps1\\n上帝视角白屏：房间模型缺失，换 room.gltf\\n收不到通知：App 活着能收，杀掉后打开补消息\\n备份恢复：停服务 → 解压 zip 覆盖 → 重启'
    },
    {
      title: '升级与迁移',
      body: '升级：先备份 → 新代码覆盖（保留 memory/persona/key）→ 重跑 setup.ps1 → 重启\\n迁移：旧电脑备份 zip → 新电脑解压覆盖 → 填 key → 跑脚本 → App 改地址\\n完整版见 docs/总教程.md'
    },""")
p.write_text(s, encoding="utf-8")
print("教程已扩展")