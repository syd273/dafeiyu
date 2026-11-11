from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\entryability\EntryAbility.ets")
s = p.read_text(encoding="utf-8")
s = s.replace("import { wantAgent, WantAgent } from '@kit.AbilityKit';",
              "import { wantAgent, WantAgent, Want } from '@kit.AbilityKit';")
s = s.replace("""      const info: wantAgent.WantAgentInfo = {
        wants: [
          {
            bundleName: 'com.anshiyu.app',
            abilityName: 'EntryAbility',
          } as wantAgent.WantAgentInfo,
        ],""",
"""      const want: Want = {
        bundleName: 'com.anshiyu.app',
        abilityName: 'EntryAbility',
      };
      const info: wantAgent.WantAgentInfo = {
        wants: [want],""")
s = s.replace("        ).catch((e) => { });\n      }).catch((e) => { });",
              "        ).catch((e: Error) => { });\n      }).catch((e: Error) => { });")
s = s.replace("      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e) => { });",
              "      backgroundTaskManager.stopBackgroundRunning(this.context).catch((e: Error) => { });")
p.write_text(s, encoding="utf-8")
print("fixed")