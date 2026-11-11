from pathlib import Path
import ast
p = Path(r"D:\大肥鱼\scripts\guardian.py")
s = p.read_text(encoding="utf-8")
if "def napcat_alive" not in s:
    s = s.replace("def established(port: int) -> bool:", '''def napcat_alive() -> bool:
    """只认 NapCat 自己的 node 进程（Adobe 等其它 node.exe 不算）"""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \\"Name='node.exe'\\" | "
             "Where-Object { $_.CommandLine -match 'napcat' } | Measure-Object | "
             "Select-Object -ExpandProperty Count"],
            capture_output=True, text=True, errors="ignore", timeout=20).stdout
        return int((out or "0").strip() or 0) > 0
    except Exception:
        return False


def established(port: int) -> bool:''')
    s = s.replace('        node_alive = proc_alive("node.exe")', '        node_alive = napcat_alive()')
    p.write_text(s, encoding="utf-8")
    ast.parse(s)
    print("guardian napcat_alive ok")