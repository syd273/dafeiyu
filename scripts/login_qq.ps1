$ErrorActionPreference = 'SilentlyContinue'
$BASE = 'D:\大肥鱼'
$QR   = 'http://127.0.0.1:8098/qr.html'

function Is-Online {
  $c = Get-NetTCPConnection -LocalPort 6199 -State Established -ErrorAction SilentlyContinue
  return ($c | Measure-Object).Count -gt 0
}
function Start-QrServer {
  $cache = "$BASE\qq\napcat\napcat\cache"
  $running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'http.server 8098' }
  if (-not $running) {
    Start-Process -WindowStyle Hidden -FilePath 'D:\Python312\python.exe' -ArgumentList '-m','http.server','8098','--bind','127.0.0.1' -WorkingDirectory $cache
    Start-Sleep -Seconds 2
  }
}
function Ensure-Services {
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
}

if (Is-Online) {
  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.MessageBox]::Show("安诗鱼已经在线，不需要扫码。", "安诗鱼", 0) | Out-Null
  exit
}

Ensure-Services
Start-QrServer

# 重启 NapCat 生成新二维码（进程在但没连上时也重启）
Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match 'napcat' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 3
Start-Process -WindowStyle Hidden -FilePath 'cmd.exe' -ArgumentList '/c','napcat.bat' -WorkingDirectory "$BASE\qq\napcat"

# 等新二维码并打开
for ($i = 0; $i -lt 25; $i++) {
  Start-Sleep -Seconds 2
  $qr = "$BASE\qq\napcat\napcat\cache\qrcode.png"
  if (Test-Path $qr) {
    $age = (Get-Date) - (Get-Item $qr).LastWriteTime
    if ($age.TotalSeconds -lt 45) { Start-Process $QR; break }
  }
}