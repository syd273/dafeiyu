import json
from pathlib import Path

# 用户协议页面（复用隐私政策结构）
src = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Privacy.ets").read_text(encoding="utf-8")
agreement = src.replace("struct Privacy {", "struct Agreement {")
agreement = agreement.replace("// 隐私政策", "// 用户协议")
agreement = agreement.replace("Text('隐私政策').fontSize(18)", "Text('用户协议').fontSize(18)")
agreement = agreement.replace("Text('🔒').fontSize(18)", "Text('📄').fontSize(18)")
# 替换章节内容
start = agreement.find("          this.section('一、我们收集什么'")
end = agreement.find("          Text('完整版见电脑上 docs/隐私政策.md')")
if start >= 0 and end >= 0:
    sections = '''          this.section('一、服务说明', '个人自用的 AI 陪伴应用：手机 App + 电脑端服务；服务端跑在你自己的电脑；对话由 DeepSeek 生成；无账号、无云端、无付费。')
          this.section('二、使用资格', '应具备完全民事行为能力；未成年人需监护人同意与陪同；需自备电脑、手机、DeepSeek API Key 与网络。')
          this.section('三、使用规则（禁止）', '不得违法；不得诈骗、骚扰、跟踪、敲诈、威胁；不得侵犯隐私（人肉/开盒/窃听）；不得生成传播违法有害内容；不得冒充他人；不得破解攻击；商业化需自行取得资质。')
          this.section('四、AI 生成内容', '她的回复由 AI 生成，不保证真实准确完整；专业问题请咨询专业人士；对外发布前自行核实；遵守当地 AI 内容标识规定。')
          this.section('五、知识产权', '自研部分 MIT 开源；聊天与记忆归你；第三方素材归原作者；AI 生成内容权利以 DeepSeek 条款为准。')
          this.section('六、隐私', '处理方式见《隐私政策》；数据存你自己设备；聊天会发给 DeepSeek；备份自行保管。')
          this.section('七、服务变更与终止', '开源项目可能随时更新或停止维护；可随时停止使用并删除全部数据；不对持续性、可用性作承诺。')
          this.section('八、免责声明', '按现状提供，无任何担保；使用导致的损失作者不担责；DeepSeek 服务问题由你与 DeepSeek 解决；你的内容与行为自行负责。')
          this.section('九、争议解决', '适用中华人民共和国法律；友好协商，协商不成提交作者所在地有管辖权法院。')
          this.section('十、联系方式', '开源项目，问题通过 GitHub Issues 反馈。')
          this.section('十一、协议更新', '更新时修改最后更新日期，继续使用即表示同意。')
'''
    agreement = agreement[:start] + sections + agreement[end:]
agreement = agreement.replace("完整版见电脑上 docs/隐私政策.md", "完整版见电脑上 docs/用户协议.md")
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Agreement.ets")
p.write_text(agreement, encoding="utf-8")
print("用户协议页面已建")

# 路由
p = Path(r"D:\anshiyu_app\entry\src\main\resources\base\profile\main_pages.json")
d = json.loads(p.read_text(encoding="utf-8"))
if "pages/Agreement" not in d["src"]:
    d["src"].append("pages/Agreement")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("路由:", d["src"])

# 设置入口
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""            Button('🔒 隐私政策')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Privacy' }); })""",
"""            Button('🔒 隐私政策')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Privacy' }); })
            Button('📄 用户协议')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#1d2a4a').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { router.pushUrl({ url: 'pages/Agreement' }); })""")
p.write_text(s, encoding="utf-8")
print("设置入口已加")

# README 链接
p = Path(r"D:\大肥鱼\README.md")
s = p.read_text(encoding="utf-8")
if "用户协议" not in s:
    s = s.replace("## 隐私政策",
"""## 用户协议

完整版见 [docs/用户协议.md](docs/用户协议.md)。

## 隐私政策""")
    p.write_text(s, encoding="utf-8")
    print("README 已加链接")