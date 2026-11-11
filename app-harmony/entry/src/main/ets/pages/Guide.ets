// 配置教程：从注册 DeepSeek 到可用
import router from '@ohos.router';

interface Step {
  title: string;
  body: string;
}

@Entry
@Component
struct Guide {
  private steps: Step[] = [
    {
      title: '① 注册 DeepSeek 开放平台',
      body: '打开 platform.deepseek.com → 注册登录 → 左侧 API keys → 创建 API key → 复制 sk- 开头的 Key（只显示一次，存好）。\n\n新用户有免费额度，长期用需要充值。'
    },
    {
      title: '② 部署后端（电脑）',
      body: '项目放到 D:\\大肥鱼\\\n\nPowerShell 执行：\nSetup:\npowershell -ExecutionPolicy Bypass -File "D:\\大肥鱼\\scripts\\setup.ps1"\n\n启动：\npowershell -ExecutionPolicy Bypass -File "D:\\大肥鱼\\scripts\\start_all.ps1"\n\n把 Key 写进 D:\\大肥鱼\\deepseek-key.txt。'
    },
    {
      title: '③ 填服务器地址',
      body: '设置 → 本地服务器 → 填 http://电脑IP:8900\n\n电脑 IP：PowerShell 执行 ipconfig，找 WLAN 的 IPv4（如 192.168.43.5）。\n\n手机和电脑要连同一个网络。'
    },
    {
      title: '④ 填连接令牌',
      body: '默认令牌 anshiyu-app-2026（仅供本地测试）。\n\n正式使用时：修改 D:\\大肥鱼\\anshiyu-server\\config.json 里的 token，然后在 App 设置 → 连接令牌 填同样的值。'
    },
    {
      title: '⑤ 填 DeepSeek Key（二选一）',
      body: '方式一：电脑上写 D:\\大肥鱼\\deepseek-key.txt\n方式二：App 设置 → DeepSeek API Key → 粘贴 → 保存 Key → 测试 Key'
    },
    {
      title: '⑥ 测试连接',
      body: '设置 → 本地服务器 → 测试连接（应显示 连接成功 ✓）\n设置 → DeepSeek API Key → 测试 Key（应显示 Key 可用 ✓）'
    },
    {
      title: '⑦ 开始使用',
      body: '聊天：首页\n说说：顶栏 💬\n星图：顶栏 ⭐\n生活记录 / 记忆记录 / 一起听歌 / 上帝视角 / 传承：设置 → 更多\n性格 / 记忆设置 / 功能开关 / 备份：设置里'
    },
    {
      title: '⑧ 可选组件（自己装）',
      body: '房间模型：把 room.gltf 放到 milky-way-3d/room/\n表情包：dsh-meme 图片放到 persona/stickers/\n\n不装也能用，页面会提示。详见 docs/可选组件.md。'
    },
    {
      title: '插件：她的房间（可选）',
      body: '从 GitHub 下载等距房间模型（.gltf，如 Aubrey-Li/cozy-room，MIT）\n重命名为 room.gltf\n放到 D:\\大肥鱼\\milky-way-3d\\room\\room.gltf\n打开上帝视角自动加载。\n不装：页面提示未安装，其他功能正常。\n关闭：设置 → 功能开关 → 房间展示。'
    },
    {
      title: '插件：表情包（可选）',
      body: '下载 dsh-meme（MIT）的图片放到 persona/stickers/\n在 persona/stickers.json 登记 id/文字/文件名\n重启网关生效。\n不装：她不发表情。\n关闭：设置 → 功能开关 → 表情包。'
    },
    {
      title: '插件：星图 / 记忆模式 / 服务器',
      body: '星图：内置，可替换 milky-way-3d 下的页面\n记忆模式：设置里切换（衰减/完全）\n服务器：本地/云端两套独立配置，接口一致'
    },
    {
      title: '故障修复（常见）',
      body: '离线：点顶栏「重连」；检查同一网络；IP 变了 App 会自动扫\n测试连接失败：服务没起/防火墙，重跑 start_all.ps1\n测试 Key 失败：Key 错/余额不足，去平台看余额\n端口被占：Get-NetTCPConnection -LocalPort 8900 → Stop-Process -Id PID -Force\n服务起不来：装 Python 3.12 + Node 20+，重跑 setup.ps1\n上帝视角白屏：房间模型缺失，换 room.gltf\n收不到通知：App 活着能收，杀掉后打开补消息\n备份恢复：停服务 → 解压 zip 覆盖 → 重启'
    },
    {
      title: '⚠️ 使用须知与合规声明',
      body: '1. 仅限个人合法使用：不得用于诈骗、骚扰、侵犯隐私、传播违法内容\n2. AI 生成内容不保证真实准确，专业问题请咨询专业人士，对外发布前自行核实\n3. 内置违法/隐私词库过滤，但不能 100% 拦截，需自行维护并遵守当地法律\n4. 聊天记忆存本地，但会发送给 DeepSeek 处理，请遵守其服务条款\n5. 备份含隐私，妥善保存；不要让她接触他人隐私信息\n6. 未成年人使用需监护人同意\n7. 第三方素材遵守其许可（MIT/Apache/仅自用）\n8. 开源 MIT 许可，按现状提供，作者不承担使用后果\n9. 做成公开产品需自行取得资质、备案、内容审核与隐私政策'
    },
    {
      title: '升级与迁移',
      body: '升级：先备份 → 新代码覆盖（保留 memory/persona/key）→ 重跑 setup.ps1 → 重启\n迁移：旧电脑备份 zip → 新电脑解压覆盖 → 填 key → 跑脚本 → App 改地址\n完整版见 docs/总教程.md'
    },
  ];

  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('配置教程').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text('📖').fontSize(18)
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      Scroll() {
        Column() {
          ForEach(this.steps, (s: Step, idx: number) => {
            Column() {
              Text(s.title)
                .fontSize(15).fontWeight(FontWeight.Medium).fontColor('#ffd48a')
                .width('100%')
              Text(s.body)
                .fontSize(12).lineHeight(19).fontColor('#cfe0ff')
                .margin({ top: 8 }).width('100%')
            }
            .width('100%').padding(14)
            .backgroundColor('#121826').borderRadius(14).margin({ top: 10 })
          }, (s: Step, idx: number) => s.title)

          Text('完整版见电脑上 docs/总教程.md')
            .fontSize(11).fontColor('#4a567c').margin({ top: 16, bottom: 20 })
        }
        .padding({ left: 16, right: 16 })
      }
      .edgeEffect(EdgeEffect.Spring)
      .layoutWeight(1)
    }
    .padding({ top: 38 })
    .width('100%')
    .height('100%')
    .backgroundColor('#0d1017')
  }
}
