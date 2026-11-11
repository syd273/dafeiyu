from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { wantAgent, WantAgent, Want } from '@kit.AbilityKit';",
              "import { wantAgent, WantAgent } from '@kit.AbilityKit';")
p.write_text(s, encoding="utf-8")
print("fixed duplicate import")