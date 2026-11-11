from pathlib import Path

# PushHelper 增加错误返回
p = Path(r"D:\anshiyu_app\entry\src\main\ets\common\PushHelper.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("""  /** 获取 Push token 并上报（失败静默） */
  static async register(baseUrl: string): Promise<string> {
    try {
      const token = await pushService.getToken();
      if (!token) return '';""",
"""  /** 获取 Push token 并上报（失败静默） */
  static async register(baseUrl: string): Promise<string> {
    try {
      const token = await pushService.getToken();
      if (!token) return '';""")
s = s.replace("""    } catch (e) {
      // 未配置 AGC 或用户未授权时返回空
      return '';
    }
  }""",
"""    } catch (e) {
      // 未配置 AGC 或用户未授权时返回空
      return '';
    }
  }

  /** 诊断：返回 token 或错误信息 */
  static async diagnose(baseUrl: string): Promise<string> {
    try {
      const token = await pushService.getToken();
      if (!token) return 'getToken 返回空（Push Kit 可能未开通）';
      try {
        const req = http.createHttp();
        const res = await req.request(`${baseUrl}/api/push/token?token=${TOKEN}`, {
          method: http.RequestMethod.POST,
          header: { 'Content-Type': 'application/json' },
          extraData: JSON.stringify({ pushToken: token }),
          connectTimeout: 8000,
          readTimeout: 8000,
        });
        req.destroy();
        return `token=${token.slice(0, 16)}… 上报=${res.responseCode === 200 ? '成功' : '失败'}`;
      } catch (e2) {
        return 'token 已获取，但上报失败（网络）';
      }
    } catch (e) {
      return 'getToken 异常：' + JSON.stringify(e);
    }
  }""")
p.write_text(s, encoding="utf-8")
print("PushHelper 诊断已加")

# 设置页加推送诊断按钮
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { ChatStore, SyncState } from '../common/ChatStore';",
"""import { ChatStore, SyncState } from '../common/ChatStore';
import { PushHelper } from '../common/PushHelper';""")
s = s.replace("""            Text('收不到的话，去系统设置里允许安诗鱼通知')
              .fontSize(11).fontColor('#5f6c96').margin({ top: 8 })""",
"""            Text('收不到的话，去系统设置里允许安诗鱼通知')
              .fontSize(11).fontColor('#5f6c96').margin({ top: 8 })
            Button('推送诊断')
              .height(30).margin({ top: 8 }).width('100%')
              .backgroundColor('#161b29').fontSize(12).fontColor('#8fa2d8')
              .borderRadius(10)
              .onClick(() => {
                PushHelper.diagnose(this.baseUrl2).then((msg: string) => {
                  this.tip = msg;
                });
              })""")
p.write_text(s, encoding="utf-8")
print("设置页诊断按钮已加")