from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\common\Notifier.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { notificationManager } from '@kit.NotificationKit';",
"""import { notificationManager } from '@kit.NotificationKit';
import { common } from '@kit.AbilityKit';""")
s = s.replace("static async ensure(ctx: Context): Promise<void> {",
              "static async ensure(ctx: common.UIAbilityContext): Promise<void> {")
p.write_text(s, encoding="utf-8")
print("Notifier fixed")

p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { Notifier } from '../common/Notifier';",
"""import { Notifier } from '../common/Notifier';
import { common } from '@kit.AbilityKit';""")
s = s.replace("Notifier.ensure(getContext(this) as Context);",
              "Notifier.ensure(getContext(this) as common.UIAbilityContext);")
p.write_text(s, encoding="utf-8")
print("Index fixed")