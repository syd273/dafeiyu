from pathlib import Path
p = Path(r"D:\大肥鱼\docs\交接-安诗鱼App.md")
s = p.read_text(encoding="utf-8")
if "受保护项目" not in s:
    s = s.replace("## 七、注意事项", """## 七、项目边界（重要）

**校枢（XiaoShuApp）是受保护项目，安诗鱼不得干扰**，详见 `docs/项目边界-不与校枢冲突.md`。

硬性规则：
1. 禁止调用/加载/卸载 Ollama（11434）的任何模型（校枢在用）
2. 禁止停止/重启校枢进程（XiaoShuApp、19000、19101、19100 CosyVoice2）
3. 禁止写校枢目录（C:\\Users\\SYD\\AppData\\Local\\XiaoShuApp、C:\\XiaoShuAgent、D:\\DHS\\DeepSeek操作中心\\work\\cosyvoice2）
4. 安诗鱼默认用 DeepSeek 云端；本地模型要独立实例（独立端口/模型文件），GPU 冲突时用 CPU 或放弃
5. 不使用 CosyVoice2；语音另建独立 TTS（非 MVP）

## 八、注意事项""")
    p.write_text(s, encoding="utf-8")
    print("handover updated")
else:
    print("already")