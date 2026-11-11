from pathlib import Path

# 1) README 加 DSH 一键部署章节
p = Path(r"D:\大肥鱼\README.md")
s = p.read_text(encoding="utf-8")
if "一键部署（DSH）" not in s:
    s = s.replace("""### 1. 配置 API Key""",
"""### 一键部署（DSH）

如果你使用 [DeepSeek Harness（DSH）](https://github.com/deepseek-ai) 作为编码代理，可以让它直接完成部署：

```text
用 DSH 打开本项目，执行：
1. powershell -ExecutionPolicy Bypass -File scripts\\setup.ps1
2. 按提示创建 deepseek-key.txt（填你的 DeepSeek API Key）
3. powershell -ExecutionPolicy Bypass -File scripts\\start_all.ps1
4. 用 DevEco Studio 打开 app-harmony/，配置签名后装到手机
```

`setup.ps1` 会自动检查 Node/Python、安装依赖、初始化配置模板；`start_all.ps1` 会拉起全部服务（Life Core、网关、星图、记忆同步）。

### 1. 配置 API Key""")
    p.write_text(s, encoding="utf-8")
    print("README 已更新")

# 2) docs/android.md
Path(r"D:\大肥鱼\docs").mkdir(exist_ok=True)
(P := Path(r"D:\大肥鱼\docs\android.md")).write_text("""# 安卓端方案

当前仓库只有鸿蒙 App（app-harmony/）。安卓端推荐用 **WebView 壳** 方案，一套 Web UI 双端运行。

## 方案

1. 把聊天、星图、生活记录、记忆记录做成 Web 页面（星图已经是 Web）
2. 安卓壳：Android WebView 加载 `http://<PC-IP>:8900/app`（本地页面）
3. 鸿蒙壳：ArkWeb 组件加载同一地址

## 最小实现（可先做）

安卓端先用 WebView 加载 8900 上的聊天测试页（见 anshiyu-server/static/），
星图用 8899 的页面。后续再把聊天页做成正式 Web UI。

## 打包

- 安卓：Android Studio 构建 APK（自签名即可）
- 鸿蒙：DevEco Studio 构建 HAP（需华为开发者签名）
- 两者都放到 GitHub Release 供下载

## 注意

- 需要允许 HTTP 明文（android:usesCleartextTraffic="true"）
- 服务器地址在 App 内可配置
""", encoding="utf-8")
print("docs/android.md 已创建")