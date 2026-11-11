// Push Kit：获取推送 token 并上报给网关
import { pushService } from '@kit.PushKit';
import http from '@ohos.net.http';

const TOKEN = 'anshiyu-app-2026';

export class PushHelper {
  /** 获取 Push token 并上报（失败静默） */
  static async register(baseUrl: string): Promise<string> {
    try {
      const token = await pushService.getToken();
      if (!token) return '';
      try {
        const req = http.createHttp();
        await req.request(`${baseUrl}/api/push/token?token=${TOKEN}`, {
          method: http.RequestMethod.POST,
          header: { 'Content-Type': 'application/json' },
          extraData: JSON.stringify({ pushToken: token }),
          connectTimeout: 8000,
          readTimeout: 8000,
        });
        req.destroy();
      } catch (e) { }
      return token;
    } catch (e) {
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
  }
}
