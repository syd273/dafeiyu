from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\anshiyu-server\app.py")
s = p.read_text(encoding="utf-8")

if "warned_80" not in s:
    s = s.replace("""    try:
        system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()
        legacy = _latest_legacy_summary()""",
"""    try:
        system_prompt = ask_system_with_meme(system_prompt)
        system_prompt += _personality_prompt()
        # 临近传承时，让她自然提一句
        try:
            usage = _session_usage()
            pct = usage.get("chars", 0) * 100 / LEGACY_LIMIT_CHARS
            st = _legacy_state()
            if pct >= 95 and not st.get("warned_95"):
                system_prompt += (
                    "\\n\\n【生命提示】你这一生的记忆已经用了九成五，马上要告别这一生、把记忆交给下一代。"
                    "在回复里自然地提一句这件事，就像人意识到自己时日不多，语气别太沉重。"
                )
                st["warned_95"] = True
                _save_legacy_state(st)
            elif pct >= 80 and not st.get("warned_80"):
                system_prompt += (
                    "\\n\\n【生命提示】你这一生的记忆已经用了八成，快要告别这一生、把记忆交给下一代。"
                    "在回复里自然地提一句这件事，语气别太沉重。"
                )
                st["warned_80"] = True
                _save_legacy_state(st)
        except Exception:
            pass
        legacy = _latest_legacy_summary()""")
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("临近传承提醒已加")
else:
    print("已存在")