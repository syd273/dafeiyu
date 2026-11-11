from pathlib import Path
p = Path(r"D:\大肥鱼\docs\开发进度.md")
s = p.read_text(encoding="utf-8")
s = s.replace("""### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 主动消息实际运行验证（等待真实触发）""",
"""### 主动消息实际运行验证完成（2026-11-10）
- 启动 Life Core + 网关，用 `scripts/ws_watch.py` 模拟 App 在线（WS 连接）
- 60 秒后主动循环首次 tick，真实触发一条主动消息：
  `阿东早呀，天阴阴的，感觉随时要下雨。我刚坐书桌这儿准备写东西呢。`
- 场景：morning（8-10 窗口） + 生活状态（书桌做事 / 天阴要下雨）
- 生成模型：云端 deepseek-chat
- 验证后清理：删除 6 条测试消息 + 6 颗对应记忆星；app_state 已恢复
- 结论：主动消息端到端链路打通（场景选择 → LLM 生成 → WS 推送 → App 收到）

### 下一步
1. 上帝视角接入鸿蒙 App（Web 组件或原生页）
2. 鸿蒙 App 聊天页（等 DevEco Studio 安装包）
3. 把主动消息记录同步到上帝视角动态流""")
p.write_text(s, encoding="utf-8")
print("progress updated")