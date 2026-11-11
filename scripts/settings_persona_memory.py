from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

# 状态
s = s.replace("  @State sharePref: string = 'both';",
"""  @State sharePref: string = 'both';
  @State talkative: number = 50;
  @State clingy: number = 50;
  @State gentle: number = 50;
  @State proactive: string = 'medium';
  @State memoryMode: string = 'decay';
  @State halfLifeDays: number = 1.08;
  @State maxEpisodes: number = 0;
  @State nightlyReflect: boolean = true;""")

# 载入
s = s.replace("    await this.loadSharePref();",
"""    await this.loadSharePref();
    await this.loadPersona();
    await this.loadMemory();""")

# 方法
s = s.replace("""  async saveSharePref(p: string) {""",
"""  async loadPersona() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/persona/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.talkative = (d.talkative ?? 50) as number;
        this.clingy = (d.clingy ?? 50) as number;
        this.gentle = (d.gentle ?? 50) as number;
        this.proactive = (d.proactive ?? 'medium') as string;
      }
    } catch (e) { }
  }

  async savePersona() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/persona/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({
          talkative: this.talkative, clingy: this.clingy, gentle: this.gentle,
          proactive: this.proactive,
        }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      this.tip = '她的性格已保存';
    } catch (e) {
      this.tip = '性格保存失败';
    }
  }

  async loadMemory() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/memory/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.memoryMode = (d.memoryMode ?? 'decay') as string;
        this.halfLifeDays = (d.halfLifeDays ?? 1.08) as number;
        this.maxEpisodes = (d.maxEpisodes ?? 0) as number;
        this.nightlyReflect = (d.nightlyReflect ?? true) as boolean;
      }
    } catch (e) { }
  }

  async saveMemory() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/memory/config?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({
          memoryMode: this.memoryMode, halfLifeDays: this.halfLifeDays,
          maxEpisodes: this.maxEpisodes, nightlyReflect: this.nightlyReflect,
        }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      this.tip = '记忆设置已保存';
    } catch (e) {
      this.tip = '记忆设置保存失败';
    }
  }

  async saveSharePref(p: string) {""")

p.write_text(s, encoding="utf-8")
print("设置页状态与方法已加")