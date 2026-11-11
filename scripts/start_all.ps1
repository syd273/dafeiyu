# Anshiyu services autostart
$ErrorActionPreference = 'SilentlyContinue'
$b = 'D:\大肥鱼'

function Test-Port($port) {
  return (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0
}

if (-not (Test-Port 8910)) {
  Start-Process -WindowStyle Hidden -FilePath 'node.exe' -ArgumentList 'src/server.mjs' -WorkingDirectory "$b\life-core" -RedirectStandardOutput "$b\life-core\data\lc.out" -RedirectStandardError "$b\life-core\data\lc.err"
}

if (-not (Test-Port 8900)) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-u','app.py' -WorkingDirectory "$b\anshiyu-server" -RedirectStandardOutput "$b\logs\app_server.log" -RedirectStandardError "$b\logs\app_server.err"
}

if (-not (Test-Port 8899)) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-u','server.py' -WorkingDirectory "$b\milky-way-3d" -RedirectStandardOutput "$b\milky-way-3d\srv.log" -RedirectStandardError "$b\milky-way-3d\srv.err"
}

$syncRunning = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'sync_memories' }
if (-not $syncRunning) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-u','sync_memories.py' -WorkingDirectory "$b\scripts" -RedirectStandardOutput "$b\logs\sync.out" -RedirectStandardError "$b\logs\sync.err"
}