// 用户协议
import router from '@ohos.router';

@Entry
@Component
struct Agreement {
  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('用户协议').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text('📄').fontSize(18)
      }
      .width('100%')
      .height(52)
      .padding({ left: 8, right: 14 })
      .backgroundColor('#11151f')

      Scroll() {
        Column() {
          Text('最后更新：2026-11-11')
            .fontSize(11).fontColor('#5f6c96').width('100%')
          Text('本应用是个人自用的开源项目，不收集你的身份信息。所有数据存在你自己的设备上（手机 + 电脑）。')
            .fontSize(13).lineHeight(21).fontColor('#cfe0ff').margin({ top: 10 }).width('100%')

          this.section('一、服务说明', '个人自用的 AI 陪伴应用：手机 App + 电脑端服务；服务端跑在你自己的电脑；对话由 DeepSeek 生成；无账号、无云端、无付费。')
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
          Text('完整版见电脑上 docs/用户协议.md')
            .fontSize(11).fontColor('#4a567c').margin({ top: 16, bottom: 30 })
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

  @Builder
  section(title: string, body: string) {
    Column() {
      Text(title).fontSize(14).fontWeight(FontWeight.Medium).fontColor('#ffd48a').width('100%')
      Text(body).fontSize(12).lineHeight(19).fontColor('#cfe0ff').margin({ top: 6 }).width('100%')
    }
    .width('100%').padding(14)
    .backgroundColor('#121826').borderRadius(14).margin({ top: 10 })
  }
}
