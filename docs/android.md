# 安卓端部署思路

> 先说结论：现有客户端是 **ArkTS / ArkUI**，代码**不能直接编译成 APK**。能复用的是**服务端接口**和**交互设计**，UI 必须重写，或者用 Web 承载。下面给三条路线，按投入从小到大排。

## 一、三条路线对比

| 路线 | 做法 | 工作量 | 体验 | 维护成本 | 适合 |
|---|---|---|---|---|---|
| **A. WebView 壳** | 用安卓 WebView 装现有的 H5 页面 | 1~3 天 | 一般（无原生手感） | 低（一套 Web） | 先跑通、内部自用 |
| **B. 原生重写** | Kotlin + Compose 重写 UI，对接同一套 API | 2~4 周 | 最好 | 中（两套 UI） | 正式发布 |
| **C. 跨端框架** | Flutter / React Native 一套代码多端 | 3~6 周 | 好 | 低（但鸿蒙仍要单独做） | 要同时上 Android + iOS |

**推荐路径**：先用 A 验证后端和接口能不能跑通，再用 B 重写核心聊天页；记忆星图无论走哪条路线都用 WebView 复用（它本来就是 Web）。

---

## 二、路线 A：WebView 壳（最快）

服务端**已经自带 H5 聊天页**：`anshiyu-server/static/index.html`，它调用的接口是 `/api/status`、`/api/history`、`/api/chat`、`/api/share`。

### 步骤

1. Android Studio → Empty Views Activity，`minSdk 26`
2. 布局里放一个 WebView
3. `AndroidManifest.xml`：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<application android:usesCleartextTraffic="true" ... >
```

4. 加载页面：

```kotlin
webView.settings.apply {
    javaScriptEnabled = true
    domStorageEnabled = true
    mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
}
webView.webViewClient = WebViewClient()
webView.loadUrl("http://192.168.x.x:8900/static/index.html")
```

5. 补三个体验点：
   - **返回键**：`onBackPressedDispatcher` 里先 `webView.canGoBack()` 再退出
   - **发图**：实现 `WebChromeClient.onShowFileChooser`
   - **星图横屏**：单独开一个 `sensorLandscape` 的 Activity 装载 `http://<ip>:8899`

### 三个必踩的坑

| 坑 | 现象 | 处理 |
|---|---|---|
| 明文 HTTP | Android 9+ 默认禁止，页面白屏 | `usesCleartextTraffic` 或 `network_security_config` 放行局域网段 |
| CORS | H5 里 `fetch` 被浏览器拦 | 服务端加 `Access-Control-Allow-Origin`，或在 WebView 内用同源相对路径（推荐，页面和 API 同 8900 端口就没这问题） |
| IP 写死 | 换 WiFi 后连不上 | 做一个设置页存地址，或照搬鸿蒙端的 `detectServer()` 扫描逻辑 |

---

## 三、路线 B：原生重写（正式发布用）

### 需要实现的接口

| 功能 | 接口 | 备注 |
|---|---|---|
| 连通性 / 状态 | `GET /api/status?token=` | 返回 `mood`、`life`，驱动顶栏"在线/平静·家·书桌" |
| 历史消息 | `GET /api/history?token=&limit=30` | 冷启动只取最近 30 条 |
| 发消息 | `POST /api/chat?token=`，body `{"text": "..."}` | 同步返回她的回复 |
| 实时消息 | `WS /ws?token=` | `type=message`（对话）、`type=say`（说说） |
| 说说列表 | `GET /api/says` | 「她的说说」页 |
| 记忆星图 | WebView → `http://<ip>:8899` | 直接复用 WebGL 页面，不用重写 |
| 推送登记 | `POST /api/push/token?token=` | 鸿蒙用 Push Kit，安卓换成厂商通道 |

### 技术选型建议

- **UI**：Kotlin + Jetpack Compose
- **网络**：OkHttp（HTTP）+ OkHttp WebSocket
- **本地存储**：Room（聊天记录）+ DataStore（设置项）
- **图片**：Coil
- **依赖注入**：不需要，这个项目规模手写单例就够

### 超时参数（照抄鸿蒙端的取值）

| 请求 | connectTimeout | readTimeout | 原因 |
|---|---|---|---|
| 状态查询 | **1.5s** | 2s | 连不上要快速失败，否则冷启动被网络拖到 9 秒（这个坑鸿蒙端踩过） |
| 聊天 | 8s | 60s | 大模型生成本身慢 |
| 历史 / 说说 | 2s | 3s | 本地服务，够快 |

### 本地服务器发现

鸿蒙端的 `detectServer()` 逻辑可以直接移植：取当前 IP 的前三段，扫描 `[5,2,6,10,20,3,4,7]` 这几个常见网关位，每个 600ms 超时并发探测 `/api/status`。

---

## 四、安卓特有的坑

| 问题 | 说明 | 处理 |
|---|---|---|
| 通知权限（Android 13+） | 不申请发不出通知 | 运行时申请 `POST_NOTIFICATIONS` |
| 后台保活 | 息屏后长连接被断 | 前台服务 + `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` + 引导用户加白名单 |
| 推送 | 国内机型无 GMS，FCM 不可用 | 接华为/小米/OPPO/vivo 厂商通道，或维持 WebSocket 长连接 |
| 横屏星图 | 默认跟随系统 | 单独 Activity 设 `sensorLandscape` |
| 明文与证书 | 局域网 http | 见路线 A 的坑 |
| 64K 方法数 | 依赖多了会超 | 开 `multiDexEnabled` |

---

## 五、发布

**国内应用市场**（华为/小米/OPPO/vivo/应用宝）需要：

1. 软件著作权证书
2. ICP 备案（有服务端的都要）
3. 隐私政策可访问链接（本项目已有静态页，见下方"服务端协议页"）
4. 各市场自己的隐私合规检测（会扫 SDK、权限申请时机）

**Google Play**：

1. `targetSdk` 需跟上当年要求
2. Data safety 表单要如实填（本项目会把聊天内容发给 DeepSeek）
3. 生成式 AI 类应用需说明内容来源与审核机制

---

## 六、服务端协议页（安卓也要用）

鸿蒙端上架时配的这两个链接，安卓各市场同样可用：

- 用户协议：<http://121.196.175.68/terms.html>
- 隐私政策：<http://121.196.175.68/privacy.html>

自建的话把 `anshiyu-server` 里的协议页放到任意静态服务器即可，注意用 **https**（多数市场强制要求）。

---

## 七、建议顺序

1. **第 1 天**：路线 A 跑通 → 确认手机能连上电脑的 8900 网关，聊天能用
2. **第 2~3 天**：把 H5 补成接近 App 的样子（气泡、输入栏、日期吸顶），或不补直接用
3. **第 2 周起**：路线 B 重写聊天页 → 设置页 → 说说页
4. **星图**全程用 WebView 复用，不要重写
5. 最后接推送与保活

---

## 附：为什么不建议直接转译 ArkTS

ArkTS 的 ArkUI 声明式语法、`@Component`/`@State` 状态模型、`Ability` 生命周期都是鸿蒙专有，没有成熟的转换到 Android 的工具链。硬转的成本高于重写，而且转出来的代码难以维护。
