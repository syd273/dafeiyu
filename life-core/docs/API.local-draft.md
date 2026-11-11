```markdown
# Life Core 服务 API 文档

## 服务说明
- 监听地址：127.0.0.1:8910
- 数据存储路径：D:\大肥鱼\life-core\data

## 错误约定
{ok:false, error}

## 接口列表

### 1. 获取服务健康状态
- **路径**：/health
- **方法**：GET
- **参数**：无
- **请求示例**：
  ```
  GET /health
  ```
- **响应示例**：
  ```json
  {ok: true, service: "Life Core", ts: "2023-04-01T12:34:56Z"}
  ```

### 2. 获取服务状态
- **路径**：/state
- **方法**：GET
- **参数**：无
- **请求示例**：
  ```
  GET /state
  ```
- **响应示例**：
  ```json
  {ok: true, service: "Life Core", version: "1.0.0", mood: {valence: 0.8, arousal: 0.5, tension: 0.2, label: "Happy"}, life: {location: "home", activity: "studying", silent: false}, episodes: [...], facts: [...], intents: [...], lastEvent: {...}}
  ```

### 3. 获取记忆
- **路径**：/memories?limit=
- **方法**：GET
- **参数**：limit（可选，整数）
- **请求示例**：
  ```
  GET /memories?limit=10
  ```
- **响应示例**：
  ```json
  {ok: true, items: [{id: "1", ts: "2023-03-30T10:00:00Z", gist: "学习", text: "学习编程", emo: "positive"}]}
  ```

### 4. 回忆
- **路径**：/recall?q=
- **方法**：GET
- **参数**：q（字符串）
- **请求示例**：
  ```
  GET /recall?q=学习
  ```
- **响应示例**：
  ```json
  {ok: true, items: [{...episode, score: 0.9}], context: {...}}
  ```

### 5. 获取日记
- **路径**：/diary
- **方法**：GET
- **参数**：无
- **请求示例**：
  ```
  GET /diary
  ```
- **响应示例**：
  ```json
  {ok: true, source: "llm", text: "今天学习了新的编程语言", count: 5}
  ```

### 6. 获取事实
- **路径**：/facts?p=&s=&limit=
- **方法**：GET
- **参数**：p（可选，字符串），s（可选，字符串），limit（可选，整数）
- **请求示例**：
  ```
  GET /facts?p=编程&s=学习&limit=5
  ```
- **响应示例**：
  ```json
  {ok: true, items: [{id: "1", s: "编程", p: "学习", o: "Python", prov: "user", ts: "2023-03-30T10:00:00Z", hits: 1, disputed: false}]}
  ```

### 7. 获取意图
- **路径**：/intents
- **方法**：GET
- **参数**：无
- **请求示例**：
  ```
  GET /intents
  ```
- **响应示例**：
  ```json
  {ok: true, items: [{id: "1", kind: "学习", object: "编程", prov: "user", state: "pending", dueAt: "2023-04-01T12:00:00Z", createdAt: "2023-03-30T10:00:00Z", doneAt: null}]}
  ```

### 8. 发送聊天
- **路径**：/chat
- **方法**：POST
- **参数**：text（字符串）
- **请求示例**：
  ```json
  POST /chat
  {
    "text": "你好"
  }
  ```
- **响应示例**：
  ```json
  {ok: true, reply: "你好！", memories: [...], ts: "2023-04-01T12:34:56Z"}
  ```

### 9. 发送事件
- **路径**：/event
- **方法**：POST
- **参数**：kind（字符串），text（字符串），emo（字符串）
- **请求示例**：
  ```json
  POST /event
  {
    "kind": "学习",
    "text": "学习编程",
    "emo": "positive"
  }
  ```
- **响应示例**：
  ```json
  {ok: true, episode: {...}, intent: {...}, mood: {...}}
  ```

### 10. 标记意图完成
- **路径**：/intent/done
- **方法**：POST
- **参数**：id（字符串）
- **请求示例**：
  ```json
  POST /intent/done
  {
    "id": "1"
  }
  ```
- **响应示例**：
  ```json
  {ok: true, intent: {...}}
  ```

### 11. 合并数据
- **路径**：/consolidate
- **方法**：POST
- **参数**：无
- **请求示例**：
  ```
  POST /consolidate
  ```
- **响应示例**：
  ```json
  {ok: true, processed: true, factsAdded: 2, intentsAdded: 1, facts: [...]}
  ```
```