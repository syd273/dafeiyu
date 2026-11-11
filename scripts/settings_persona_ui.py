from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

ui = '''          // 她的性格
          Column() {
            Text('🎭  她的性格').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Text('话少').fontSize(11).fontColor('#5f6c96').width(30)
              Slider({ value: this.talkative, min: 0, max: 100, style: SliderStyle.OutSet })
                .layoutWeight(1)
                .selectedColor('#3b6ef5')
                .onChange((v: number, mode: SliderChangeMode) => {
                  this.talkative = Math.round(v);
                  if (mode === SliderChangeMode.End) { this.savePersona(); }
                })
              Text('话多').fontSize(11).fontColor('#5f6c96').width(30)
            }
            .width('100%').margin({ top: 6 })
            Row() {
              Text('独立').fontSize(11).fontColor('#5f6c96').width(30)
              Slider({ value: this.clingy, min: 0, max: 100, style: SliderStyle.OutSet })
                .layoutWeight(1)
                .selectedColor('#8b5cf6')
                .onChange((v: number, mode: SliderChangeMode) => {
                  this.clingy = Math.round(v);
                  if (mode === SliderChangeMode.End) { this.savePersona(); }
                })
              Text('黏人').fontSize(11).fontColor('#5f6c96').width(30)
            }
            .width('100%').margin({ top: 4 })
            Row() {
              Text('毒舌').fontSize(11).fontColor('#5f6c96').width(30)
              Slider({ value: this.gentle, min: 0, max: 100, style: SliderStyle.OutSet })
                .layoutWeight(1)
                .selectedColor('#ec4899')
                .onChange((v: number, mode: SliderChangeMode) => {
                  this.gentle = Math.round(v);
                  if (mode === SliderChangeMode.End) { this.savePersona(); }
                })
              Text('温柔').fontSize(11).fontColor('#5f6c96').width(30)
            }
            .width('100%').margin({ top: 4 })
            Row() {
              Text('主动频率').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('少').fontSize(12)
                .fontColor(this.proactive === 'low' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.proactive === 'low' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.proactive = 'low'; this.savePersona(); })
              Text('中').fontSize(12)
                .fontColor(this.proactive === 'medium' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.proactive === 'medium' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.proactive = 'medium'; this.savePersona(); })
              Text('多').fontSize(12)
                .fontColor(this.proactive === 'high' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.proactive === 'high' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.proactive = 'high'; this.savePersona(); })
            }
            .width('100%').margin({ top: 10 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 记忆设置
          Column() {
            Text('🧠  记忆设置').fontSize(12).fontColor('#7f95c8').width('100%')
            Row() {
              Text('记忆模式').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('完全').fontSize(12)
                .fontColor(this.memoryMode === 'full' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.memoryMode === 'full' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.memoryMode = 'full'; this.saveMemory(); })
              Text('衰减').fontSize(12)
                .fontColor(this.memoryMode === 'decay' ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.memoryMode === 'decay' ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.memoryMode = 'decay'; this.saveMemory(); })
            }
            .width('100%').margin({ top: 10 })
            Row() {
              Text('遗忘速度').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('慢').fontSize(12)
                .fontColor(this.halfLifeDays >= 2 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.halfLifeDays >= 2 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.halfLifeDays = 3; this.saveMemory(); })
              Text('中').fontSize(12)
                .fontColor(this.halfLifeDays > 0.6 && this.halfLifeDays < 2 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.halfLifeDays > 0.6 && this.halfLifeDays < 2 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.halfLifeDays = 1.08; this.saveMemory(); })
              Text('快').fontSize(12)
                .fontColor(this.halfLifeDays <= 0.6 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 12, right: 12, top: 5, bottom: 5 })
                .backgroundColor(this.halfLifeDays <= 0.6 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.halfLifeDays = 0.5; this.saveMemory(); })
            }
            .width('100%').margin({ top: 8 })
            Row() {
              Text('记忆上限').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Text('500').fontSize(12)
                .fontColor(this.maxEpisodes === 500 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.maxEpisodes === 500 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .onClick(() => { this.maxEpisodes = 500; this.saveMemory(); })
              Text('1000').fontSize(12)
                .fontColor(this.maxEpisodes === 1000 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.maxEpisodes === 1000 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.maxEpisodes = 1000; this.saveMemory(); })
              Text('不限').fontSize(12)
                .fontColor(this.maxEpisodes === 0 ? '#ffffff' : '#8fa2d8')
                .padding({ left: 10, right: 10, top: 5, bottom: 5 })
                .backgroundColor(this.maxEpisodes === 0 ? '#3b6ef5' : '#161b29')
                .borderRadius(12)
                .margin({ left: 8 })
                .onClick(() => { this.maxEpisodes = 0; this.saveMemory(); })
            }
            .width('100%').margin({ top: 8 })
            Row() {
              Text('夜间反思').fontSize(12).fontColor('#8fa2d8').layoutWeight(1)
              Toggle({ type: ToggleType.Switch, isOn: this.nightlyReflect })
                .selectedColor('#3b6ef5')
                .onChange((v: boolean) => { this.nightlyReflect = v; this.saveMemory(); })
            }
            .width('100%').margin({ top: 8 })
          }
          .width('100%').padding(16).backgroundColor('#121826').borderRadius(16).margin({ top: 12 })

          // 聊天记录'''

s = s.replace("          // 聊天记录", ui, 1)
p.write_text(s, encoding="utf-8")
print("性格与记忆UI已加")