# 安卓端方案

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
