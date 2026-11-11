from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Settings.ets")
s = p.read_text(encoding="utf-8")

# 新状态
s = s.replace("  @State diagMsg: string = '';",
"""  @State diagMsg: string = '';
  @State localTestMsg: string = '';
  @State cloudTestMsg: string = '';
  @State apiKeyInput: string = '';
  @State keyConfigured: boolean = false;
  @State keyMasked: string = '';
  @State keyMsg: string = '';""")

# 载入 key
s = s.replace("    await this.loadMemory();", "    await this.loadMemory();\n    await this.loadApiKey();")

# 方法
s = s.replace("  async loadPersona() {",
"""  async loadApiKey() {
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/config/api-key?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 6000, readTimeout: 6000,
      });
      req.destroy();
      if (res.responseCode === 200) {
        const d = JSON.parse(res.result as string) as Record<string, Object>;
        this.keyConfigured = (d.configured ?? false) as boolean;
        this.keyMasked = (d.masked ?? '') as string;
      }
    } catch (e) { }
  }

  async saveApiKey() {
    const k = this.apiKeyInput.trim();
    if (!k) { this.keyMsg = '请输入 API Key'; return; }
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/config/api-key?token=anshiyu-app-2026`, {
        method: http.RequestMethod.POST,
        header: { 'Content-Type': 'application/json' },
        extraData: JSON.stringify({ apiKey: k }),
        connectTimeout: 8000, readTimeout: 8000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      if (d.ok) {
        this.keyConfigured = true;
        this.keyMasked = (d.masked ?? '') as string;
        this.apiKeyInput = '';
        this.keyMsg = '已保存（只存在你的电脑上）';
      } else {
        this.keyMsg = (d.error ?? '保存失败') as string;
      }
    } catch (e) {
      this.keyMsg = '保存失败，检查网络';
    }
  }

  async testApiKey() {
    this.keyMsg = '测试中…';
    try {
      const req = http.createHttp();
      const res = await req.request(`${this.baseUrl2}/api/config/api-key/test?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 8000, readTimeout: 30000,
      });
      req.destroy();
      const d = JSON.parse(res.result as string) as Record<string, Object>;
      this.keyMsg = d.ok ? 'Key 可用 ✓' : `Key 不可用（${d.error ?? d.status ?? '未知'}）`;
    } catch (e) {
      this.keyMsg = '测试失败，检查网络';
    }
  }

  async testServer(url: string, which: string) {
    const u = url.trim();
    if (!u) return;
    const msg = which === 'local' ? 'localTestMsg' : 'cloudTestMsg';
    try {
      const req = http.createHttp();
      const res = await req.request(`${u}/api/status?token=anshiyu-app-2026`, {
        method: http.RequestMethod.GET, connectTimeout: 4000, readTimeout: 4000,
      });
      req.destroy();
      const ok = res.responseCode === 200;
      if (which === 'local') { this.localTestMsg = ok ? '连接成功 ✓' : `连接失败（${res.responseCode}）`; }
      else { this.cloudTestMsg = ok ? '连接成功 ✓' : `连接失败（${res.responseCode}）`; }
    } catch (e) {
      if (which === 'local') { this.localTestMsg = '连接失败'; } else { this.cloudTestMsg = '连接失败'; }
    }
  }

  async loadPersona() {""")

p.write_text(s, encoding="utf-8")
print("Key 与测试方法已加")