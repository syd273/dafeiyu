// 本地通知：她主动发消息时提醒
import { notificationManager } from '@kit.NotificationKit';
import { common } from '@kit.AbilityKit';

export class Notifier {
  private static seq: number = 1000;

  /** 请求通知授权（首次启动） */
  static async ensure(ctx: common.UIAbilityContext): Promise<void> {
    try {
      await notificationManager.requestEnableNotification(ctx);
    } catch (e) { }
  }

  /** 发一条通知 */
  static async notify(title: string, text: string): Promise<void> {
    try {
      Notifier.seq = (Notifier.seq + 1) % 100000;
      const request: notificationManager.NotificationRequest = {
        id: Notifier.seq,
        content: {
          notificationContentType: notificationManager.ContentType.NOTIFICATION_CONTENT_BASIC_TEXT,
          normal: {
            title: title,
            text: text,
          },
        },
      };
      await notificationManager.publish(request);
    } catch (e) { }
  }
}
