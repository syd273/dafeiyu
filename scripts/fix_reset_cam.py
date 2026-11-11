from pathlib import Path
p = Path(r"D:\大肥鱼\milky-way-3d\main.js")
s = p.read_text(encoding="utf-8")
s = s.replace("""      $('chkSpin').checked = true; spinOn = true;
      $('chkCruise').checked = true; controls.autoRotate = true;
      controls.reset();
      controls.update();""",
"""      $('chkSpin').checked = true; spinOn = true;
      $('chkCruise').checked = true; controls.autoRotate = true;
      // 恢复到开场结束后的舒适视角（不是开场前的远景）
      camera.position.set(38, 62, 158);
      controls.target.set(0, 0, 0);
      controls.update();""")
p.write_text(s, encoding="utf-8")
print("重置视角已修复")