# Life Core API 文档（v0.3）

> 服务：安诗鱼 Life Core  
> 监听：`http://127.0.0.1:8910`（仅本机回环）  
> 数据：只写 `D:\大肥鱼\life-core\data\`  
> 鉴权：当前无（仅回环访问）；接网关后可加 Token

## 错误约定

所有接口失败时返回：

```json
{ "ok": false, "error": "错误说明" }
```

HTTP 状态码：400 参数错误、404 路径不存在、405 方法不支持、500 内部错误。

---

## 1. 健康检查

`GET /health`

响应：

```json
{ "ok": true, "service": "anshiyu-life-core", "ts": 1794238632980 }
```

## 2. 状态

`GET /state`

响应：

```json
{
  "ok": true,
  "service": "anshiyu-life-core",
  "version": 3,
  "mood": { "valence": 0.2, "arousal": 0.4, "tension": 0, "label": "高兴" },
  "life": { "location": "家 · 卧室", "activity": "发呆", "silent": false },
  "episodes": 12,
  "facts": 4,
  "intents": 1,
  "lastEvent": { "kind": "life", "text": "下午在阳台晒太阳", "ts": 1794238632980 }
}
```

## 3. 记忆列表

`GET /memories?limit=10`

参数：`limit` 1~200，默认 10。

响应：

```json
{
  "ok": true,
  "items": [
    { "id": "ep_...", "ts": 1794238632980, "gist": "（开心）刷到一个好笑的小猫视频", "text": "...", "emo": "开心" }
  ]
}
```

## 4. 检索记忆

`GET /recall?q=好笑的视频`

响应：

```json
{
  "ok": true,
  "items": [
    { "id": "ep_...", "ts": 1794238632980, "score": 0.565, "gist": "（开心）刷到一个好笑的小猫视频", "text": "...", "emo": "开心" }
  ],
  "context": "- [2026/11/10 09:00:00] （开心）刷到一个好笑的小猫视频"
}
```

评分维度：字面匹配 0.42、时间衰减 0.14（半衰期 26h）、显著性 0.20、情绪强度 0.18、召回次数 0.06。

## 5. 生成日记

`GET /diary`

- 有 LLM Key：`source: "llm"`，由模型生成
- 无 Key / 调用失败：`source: "template"`，模板兜底

响应：

```json
{ "ok": true, "source": "llm", "text": "刚在阳台晒了会儿太阳……", "count": 3 }
```

## 6. 事实查询

`GET /facts?p=food.eat&s=阿东&limit=50`

参数（均可选）：`p` 谓词、`s` 主体、`limit` 默认 50。

响应：

```json
{
  "ok": true,
  "items": [
    { "id": "f_...", "s": "阿东", "p": "food.eat", "o": "番茄炒蛋", "prov": "ep_...", "ts": 1794238632980, "hits": 1, "disputed": false }
  ]
}
```

谓词闭集：`food.eat` `activity.do` `plan.go` `mood.state` `media.like` `preference.like` `health.state` `note`

## 7. 意图列表

`GET /intents`

响应：

```json
{
  "ok": true,
  "items": [
    { "id": "i_...", "kind": "intent", "object": "答应明天陪阿东看视频", "prov": "ep_...", "state": "open", "dueAt": 1794247632980, "createdAt": 1794238632980, "doneAt": 0 }
  ]
}
```

状态：`open` / `done` / `failed`；类型：`intent` / `wish` / `blocked`。

## 8. 聊天

`POST /chat`

```json
{ "text": "看视频" }
```

响应：

```json
{ "ok": true, "reply": "（life-core v0.3）关于\"看视频\"，我想起：……", "memories": [...], "ts": 1794238632980 }
```

## 9. 写生活事件

`POST /event`

```json
{ "kind": "life", "text": "今天中午吃了番茄炒蛋", "emo": "开心" }
```

响应：

```json
{
  "ok": true,
  "episode": { "id": "ep_...", "gist": "（开心）今天中午吃了番茄炒蛋", "emo": "开心", "salience": 0.55 },
  "intent": null,
  "mood": { "valence": 0.28, "arousal": 0.42, "tension": 0, "label": "高兴" }
}
```

若文本含「答应/一定/明天要…」会同时建意图并返回 `intent`。

## 10. 意图完成

`POST /intent/done`

```json
{ "id": "i_..." }
```

响应：

```json
{ "ok": true, "intent": { "id": "i_...", "state": "done", "doneAt": 1794238632980 } }
```

## 11. 巩固（情景 → 事实/意图）

`POST /consolidate`

```json
{}
```

响应：

```json
{ "ok": true, "processed": 3, "factsAdded": 2, "intentsAdded": 1, "facts": [...] }
```

幂等：已处理的情景记录在 `data/consolidated.jsonl`，重复调用不会重复抽取。

---

## 数据文件

| 文件 | 内容 |
|---|---|
| `data/episodes.jsonl` | 情景记忆（append-only） |
| `data/facts.json` | 语义事实 |
| `data/intents.json` | 意图账本 |
| `data/consolidated.jsonl` | 已巩固情景 id |
| `data/strength.json` | 记忆强度/召回次数 |
| `data/affect.json` | 情绪状态 |
| `data/state.json` | 生活状态快照 |
| `data/config.json` | LLM 配置（用户自填，不入库） |
