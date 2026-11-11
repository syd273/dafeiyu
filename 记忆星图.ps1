$ErrorActionPreference = 'SilentlyContinue'
$BASE = 'D:\大肥鱼'
$URL  = 'http://localhost:8899'
$QR   = 'http://127.0.0.1:8098/qr.html'

function Test-Alive($u) {
  try { $r = Invoke-WebRequest -Uri $u -TimeoutSec 2 -UseBasicParsing; return ($r.StatusCode -eq 200) } catch { return $false }
}
function Start-QrServer {
  $cache = "$BASE\qq\napcat\napcat\cache"
  $running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'http.server 8098' }
  if (-not $running) {
    Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-m','http.server','8098','--bind','127.0.0.1' -WorkingDirectory $cache
  }
}

if (-not (Test-Alive $URL)) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList 'server.py' -WorkingDirectory "$BASE\milky-way-3d"
  Start-Sleep -Seconds 3
}
if (-not (Get-Process astrbot -ErrorAction SilentlyContinue)) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\Scripts\astrbot.exe' -ArgumentList 'run' -WorkingDirectory "$BASE\AstrBot"
}
$sync = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'sync_memories' }
if (-not $sync) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-u',"$BASE\scripts\sync_memories.py"
}
$guard = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'guardian' }
if (-not $guard) {
  Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-u',"$BASE\scripts\guardian.py"
}
Start-QrServer

# NapCat：开机不自动登录（需要时用桌面「登录安诗鱼」）

$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$udd  = Join-Path $env:LOCALAPPDATA 'DafeiyuStarmap'
if (Test-Path (Join-Path $udd 'SingletonLock')) { Remove-Item (Join-Path $udd 'SingletonLock') -Force -ErrorAction SilentlyContinue }
$args = @("--app=$URL", "--user-data-dir=$udd", '--no-first-run', '--no-default-browser-check', '--window-size=1680,1000')
Start-Process -FilePath $edge -ArgumentList $args