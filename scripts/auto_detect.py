from pathlib import Path
p = Path(r"D:\anshiyu_app\entry\src\main\ets\pages\Index.ets")
s = p.read_text(encoding="utf-8")

# 自动探测方法
s = s.replace("""  async loadStatus() {""",
"""  /** 当前地址连不上时，扫描热点常见 IP 找服务器 */
  async detectServer(): Promise<boolean> {
    try {
      const m = this.baseUrl.match(/^(https?:\\/\\/)(\\d+\\.\\d+\\.\\d+)\\./);
      if (!m) return false;
      const prefix = `${m[1]}${m[2]}.`;
      const candidates = [5, 2, 6, 10, 20, 3, 4, 7, 8, 9, 11, 12, 15, 30, 50];
      const tasks: Promise<string>[] = [];
      for (const n of candidates) {
        tasks.push(this.probe(`${prefix}${n}:8900`));
      }
      const results = await Promise.all(tasks);
      const found = results.find((r: string) => r !== '');
      if (found) {
        this.baseUrl = found;
        const ctx = getContext(this) as Context;
        await AppConfig.setLocal(ctx, found);
        return true;
      }
    } catch (e) { }
    return false;
  }

  async probe(base: string): Promise<string> {
    try {
      const req = http.createHttp();
      const res = await req.request(`${base}/api/status?token=${TOKEN}`, {
        method: http.RequestMethod.GET,
        connectTimeout: 1500,
        readTimeout: 1500,
      });
      req.destroy();
      if (res.responseCode === 200) return base;
    } catch (e) { }
    return '';
  }

  async loadStatus() {""")

# loadStatus 失败时探测
s = s.replace("""    } catch (e) {
      this.online = false;
    }
  }""",
"""    } catch (e) {
      this.online = false;
      // 地址可能变了（热点重新分配 IP），自动找一下服务器
      this.detectServer().then((ok: boolean) => {
        if (ok) {
          this.loadStatus();
          this.connectWs();
        }
      });
    }
  }""")

# 重连按钮也先探测
s = s.replace("""          onRefresh: () => { this.loadConfig().then(() => { this.loadStatus(); this.connectWs(); }); },""",
"""          onRefresh: () => {
            this.detectServer().then((ok: boolean) => {
              if (!ok) {
                this.loadConfig().then(() => { this.loadStatus(); this.connectWs(); });
              } else {
                this.loadStatus();
                this.connectWs();
              }
            });
          },""")
p.write_text(s, encoding="utf-8")
print("自动探测已加")