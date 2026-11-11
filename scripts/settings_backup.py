from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

s = s.replace("  @State featTrends: boolean = true;",
              "  @State featTrends: boolean = true;\n  @State backupMsg: string = '';\n  @State backupFiles: string = '';")

s = s.replace("    await this.loadFeatures();", "    await this.loadFeatures();\n    await this.loadBackups();")

s = s.replace("  async saveFeature(key: string, value: boolean) {",
"""  async loadBackups() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/backup/list?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 6000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        const items = (d.items ?? []) as Array<Record<string, Object>>;
        let text = '';
        for (let i = 0; i < Math.min(items.length, 3); i++) {
          const it = items[i];
          const kb = Math.round(((it.size ?? 0) as number) / 1024);
          text += `${it.file}（${kb} KB）\\n`;
        }
        this.backupFiles = text;
      }
    } catch (e) { }
  }

  async backupNow() {
    this.backupMsg = '打包中…';
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/backup/export?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST, connectTimeout: 10000, readTimeout: 60000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        const kb = Math.round(((d.size ?? 0) as number) / 1024);
        this.backupMsg = `已备份：${d.file}（${kb} KB）\\n电脑里：D:\\\\大肥鱼\\\\backups\\\\`;
        await this.loadBackups();
      } else {
        this.backupMsg = '备份失败';
      }
    } catch (e) {
      this.backupMsg = '备份失败，检查网络';
    }
  }

  async saveFeature(key: string, value: boolean) {""")

# UI：备份卡片（放在"更多"之后）
s = s.replace("""          // 更多""",
"""          // 备份与导出
          Column() {
            Text('💾  备份与导出').fontSize(12).fontColor('#7f95c8').width('100%')
            Text('把她的记忆、聊天、日记、传承打包成一个 zip（存在电脑上）')
              .fontSize(10).fontColor('#5f6c96').margin({ top: 6 }).width('100%')
            Button('立即备份')
              .height(36).width('100%').margin({ top: 10 })
              .backgroundColor('#232d47').fontSize(13).fontColor('#cfe0ff')
              .borderRadius(12)
              .onClick(() => { this.backupNow(); })
            if (this.backupMsg) {
              Text(this.backupMsg).fontSize(11).fontColor('#ffd48a').margin({ top: 8 }).width('100%').maxLines(3)
            }
            if (this.backupFiles) {
              Text('最近备份：').fontSize(10).fontColor('#5f6c96').margin({ top: 8 }).width('100%')
              Text(this.backupFiles).fontSize(10).fontColor('#8fa2d8').width('100%').maxLines(4)
            }
            Text('⚠️ 备份含聊天隐私，请妥善保存；恢复时解压覆盖对应目录')
              .fontSize(10).fontColor('#4a567c').margin({ top: 8 }).width('100%')
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 更多""")
p.write_text(s, encoding="utf-8")
print("备份卡片已加")