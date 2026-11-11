# 安诗鱼 App 项目 · 交接文档

> 项目目标：把「安诗鱼」从 QQ 机器人升级为**自有 App**（鸿蒙原生），带上帝视角、记忆星图、自主生活（刷 B 站/抖音、主动分享），可开源自托管，用户自选本地电脑或云服务器、自填 API Key。

## 一、当前进度（2026-11-07）

| 模块 | 状态 |
|---|---|
| 后端服务（FastAPI） | ✅ 已跑通，`http://127.0.0.1:8900` |
| 聊天接口 | ✅ 实测通过（含人格、生活状态、记忆检索） |
| B 站「刷+分享」 | ✅ 实测通过（热门视频 + 感想 + 链接） |
| 抖音「刷+分享」 | ✅ 实测通过（热榜词 + 感想 + 搜索链接） |
| 历史 / 状态 / 动态 / 星图接口 | ✅ 已实现 |
| WebSocket 实时推送 | ✅ 已实现 |
| App 版主动消息循环 | ✅ 已实现 |
| 网页测试聊天页 | ✅ `http://127.0.0.1:8900/` |
| 鸿蒙 App | ⬜ 未开始（缺 DevEco Studio，需用户登录华为账号下载安装包） |
| 上帝视角 | ⬜ 未开始（设计已定：状态面板 + 房间场景 + 时间轴 + 屏幕 + 动态 + 星图 + 聊天 + 控制台） |
| 开源自托管仓库结构 | ⬜ 未开始 |
| 手机端下载网站 | ⬜ 未开始 |

## 二、运行中的服务

| 服务 | 端口 | 启动方式 |
|---|---|---|
| 安诗鱼后端（新） | 8900 | `D:\Python312\python.exe -u D:\大肥鱼\anshiyu-server\app.py` |
| 记忆星图 Web | 8899 | `python server.py`（`D:\大肥鱼\milky-way-3d`） |
| 旧 QQ 机器人栈 | 6199 | AstrBot + NapCat（保留，可继续用 QQ 通道） |

## 三、关键文件

```
D:\大肥鱼\
├─ anshiyu-server\
│  ├─ app.py              # 后端：聊天/主动/媒体/星图/WS
│  ├─ config.json         # port/token/DeepSeek key 路径/model
│  └─ static\index.html   # 网页测试聊天页
├─ persona\
│  ├─ persona.json        # 人格配置（名字、性格、口头禅、规则）
│  ├─ persona_core.py     # 人格提示词 + 心情状态机
│  ├─ life.json           # 作息表、事件池、计划模板
│  ├─ life_core.py        # 生活引擎（此刻/日程/说说/被吵醒）
│  ├─ retention.py        # 艾宾浩斯保持度
│  ├─ bili.py             # B 站热门抓取
│  ├─ douyin.py           # 抖音热榜抓取
│  ├─ proactive.json      # 主动消息配置
│  └─ owner.json          # 用户名字
├─ memory\
│  ├─ archive.db          # 记忆库（SQLite）
│  └─ kernel.py           # 记忆内核（消息/实体/情绪/检索）
├─ milky-way-3d\          # 3D 记忆星图
├─ AstrBot\ + qq\napcat\  # 旧 QQ 通道（保留）
└─ docs\                  # 安全策略、本交接文档
```

## 四、后端接口

鉴权：`?token=anshiyu-app-2026`（或请求头 X-Token）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/ping` | 健康检查 |
| GET | `/api/status` | 她此刻/心情/名字/消息数 |
| GET | `/api/history?limit=50` | 聊天记录 |
| POST | `/api/chat` `{"text":"..."}` | 聊天，返回 `{reply, mood, life}` |
| GET | `/api/feed` | 她的说说 |
| GET | `/api/stars` | 记忆星图数据 |
| POST | `/api/share/bili` | 让她刷 B 站并分享 |
| POST | `/api/share/douyin` | 让她刷抖音并分享 |
| WS | `/ws?token=...` | 实时消息（聊天 + 主动推送） |

## 五、已验证的测试记录

- 聊天：`在吗？我今天有点累` → 「在。累的话先别硬撑，坐会儿，喝口水。」（带生活状态）
- B 站分享：返回视频标题、她的感想、视频链接
- 抖音分享：返回热榜词、她的感想、抖音搜索链接

## 六、下一步（优先级）

1. **装 DevEco Studio**（需用户登录华为账号下载，当前最大阻塞）
2. 建鸿蒙工程 `app-harmony/`：聊天页、动态页、星图页（Web 组件嵌入 8899）、上帝视角页
3. 上帝视角：状态面板 + 房间场景 + 24h 时间轴 + 她正在刷的视频 + 动态流 + 星图
4. 后端增强：抖音/B 站主动分享加入 proactive 类型；上帝视角数据接口（当前屏幕/动画状态）
5. 开源自托管仓库：`core/ server/ web/ app-harmony/ deploy/ docs/`，Docker compose + 一键脚本 + API Key 配置向导
6. 手机端下载网站 + App 发布（AppGallery 需资质，见对话中的上架门槛说明）

## 七、项目边界（重要）

**校枢（XiaoShuApp）是受保护项目，安诗鱼不得干扰**，详见 `docs/项目边界-不与校枢冲突.md`。

硬性规则：
1. 禁止调用/加载/卸载 Ollama（11434）的任何模型（校枢在用）
2. 禁止停止/重启校枢进程（XiaoShuApp、19000、19101、19100 CosyVoice2）
3. 禁止写校枢目录（C:\Users\SYD\AppData\Local\XiaoShuApp、C:\XiaoShuAgent、D:\DHS\DeepSeek操作中心\work\cosyvoice2）
4. 安诗鱼默认用 DeepSeek 云端；本地模型要独立实例（独立端口/模型文件），GPU 冲突时用 CPU 或放弃
5. 不使用 CosyVoice2；语音另建独立 TTS（非 MVP）

## 八、注意事项

- 用户华为手机是**鸿蒙 7.0（纯血鸿蒙）**，不能装安卓 APK，必须做 HAP；用户有华为开发者账号（初级认证）
- 旧安卓备用机可用于 APK 验证
- 用户要求：开源自托管、用户在 DHS（AI 助手）里一键部署、本地/云自选、API Key 自填
- 用户对"记忆清零/第一次见面"要求严格：会多次要求清空记忆（`scripts/clear_all.py` 可复用）
- 网页测试入口是临时的，最终交付是鸿蒙 App
- QQ 通道仍可保留并行，但新 App 不依赖 QQ/NapCat


## 九、模型分工约定（2026-11-07 用户确认）

- 聊天/主动消息/分享内容 → **DeepSeek 云端**
- 写代码任务 → **本地 qwen3.5:9b**（仅校枢空闲时，经 `local_llm.py` 借调）
  - HTTP：`POST /api/code`
  - CLI：`python local_code.py`
- 校枢占用时一律不借调，返回 busy


## 十、交互约定（用户明确要求）

**当任务处于"本地模型能力 ≈ 云端模型能力"区间时，必须问用户用本地还是云端，按用户选择执行。**

详见 `docs/交互约定.md`。
- 适用：写代码、短文案、总结、分类、简单问答
- 不适用：长上下文/复杂推理（云端）、仅本地能做的任务（说明原因）
- ✅ 已确认：App 实时聊天 = **云端优先**（cloud_first），云端失败才本地兜底；开发任务仍每次问用户


## 十一、开发铁律（用户明确要求）

见 `docs/开发铁律.md`：
- 能力接近时交本地 qwen2.5-coder:7b（校枢空闲时），大型代码类任务也可以，中途可反问
- 不影响电脑运行、不干扰 DSH、只写 D:\大肥鱼、绝对隔离校枢
