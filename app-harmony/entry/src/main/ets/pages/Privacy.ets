// 隐私政策
import router from '@ohos.router';

@Entry
@Component
struct Privacy {
  build() {
    Column() {
      Row() {
        Text('‹').fontSize(28).fontColor('#9fc1ff').width(34).textAlign(TextAlign.Center)
          .onClick(() => { router.back(); })
        Text('隐私政策').fontSize(18).fontWeight(FontWeight.Medium).fontColor('#e8eeff')
        Blank()
        Text('🔒').fontSize(18)
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

          this.section('一、我们收集什么', '不收集：姓名、手机号、身份证、位置、通讯录、设备标识。\n本地保存：聊天记录（手机）、记忆（电脑 memory/）、星图数据、偏好设置、API Key、备份。')
          this.section('二、信息如何使用', '聊天内容会作为上下文发送给 DeepSeek（第三方大模型）生成回复；记忆只用于本地，不上传；API Key 只用于调用 DeepSeek。')
          this.section('三、第三方共享', '仅 DeepSeek（聊天上下文）与华为推送（如启用，通知 token）。不会向任何第三方出售、出租或共享你的信息。')
          this.section('四、数据安全', '所有数据存在你自己的设备；API Key 文件设置了系统权限；备份含隐私请妥善保管；不要用公共电脑/网络进行敏感对话。')
          this.section('五、你的权利', '查看：聊天/记忆/生活记录/说说\n删除记忆：设置 → 记忆记录 → 删除\n清空聊天：设置 → 清空聊天记录（记忆保留）\n导出：设置 → 备份与导出\n删除全部：删除 App + 电脑 memory/persona/backups')
          this.section('六、未成年人', '需监护人同意与陪同使用，不要生成不适合未成年人的内容。')
          this.section('七、内容与合规', '内置违法/隐私词库过滤但不能 100% 拦截；遵守所在地法律法规，不得用于违法用途；AI 内容仅供参考。')
          this.section('八、政策变更', '更新时修改最后更新日期，继续使用即表示同意。')
          this.section('九、联系方式', '开源项目，问题通过 GitHub Issues 反馈（见 README）。')

          Text('完整版见电脑上 docs/隐私政策.md')
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
