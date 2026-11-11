# Anshiyu one-click setup. Run by DSH or manually:
#   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Write-Host "== Anshiyu setup ==" -ForegroundColor Cyan
Write-Host "Project: $root"

# 1) Node
try {
  $node = & node --version 2>$null
  if ($node) { Write-Host "[OK] Node $node" -ForegroundColor Green }
  else { Write-Host "[MISS] Node.js not found. Install Node 18+ from https://nodejs.org/" -ForegroundColor Red }
} catch {
  Write-Host "[MISS] Node.js not found." -ForegroundColor Red
}

# 2) Python
$py = $null
foreach ($p in @('python','py','D:\Python312\python.exe')) {
  try {
    $v = & $p --version 2>$null
    if ($v -match 'Python 3') { $py = $p; Write-Host "[OK] $v ($p)" -ForegroundColor Green; break }
  } catch { }
}
if (-not $py) { Write-Host "[MISS] Python 3.10+ not found." -ForegroundColor Red }

# 3) Python deps
if ($py) {
  Write-Host "Installing Python deps (fastapi uvicorn requests) ..."
  & $py -m pip install --quiet fastapi uvicorn requests 2>&1 | ForEach-Object { if ($_ -match 'ERROR') { Write-Host $_ -ForegroundColor Red } }
  Write-Host "[OK] Python deps installed" -ForegroundColor Green
}

# 4) API key
$keyFile = Join-Path $root 'deepseek-key.txt'
if (-not (Test-Path $keyFile)) {
  Write-Host "[TODO] Create deepseek-key.txt in project root, content: your DeepSeek API key (sk-...)" -ForegroundColor Yellow
} else {
  $k = (Get-Content $keyFile -Raw).Trim()
  if ($k.Length -gt 10) { Write-Host "[OK] DeepSeek API key found" -ForegroundColor Green }
  else { Write-Host "[TODO] deepseek-key.txt looks empty" -ForegroundColor Yellow }
}

# 5) persona config (copy templates if missing)
$persona = Join-Path $root 'persona'
$tpl = Join-Path $persona 'templates'
foreach ($f in @('life.json','proactive.json')) {
  $target = Join-Path $persona $f
  if (-not (Test-Path $target) -and (Test-Path (Join-Path $tpl $f))) {
    Copy-Item (Join-Path $tpl $f) $target
    Write-Host "[INIT] persona/$f from template" -ForegroundColor Green
  }
}

# 6) data dirs
foreach ($d in @('life-core\data','memory','logs','milky-way-3d\life')) {
  $p = Join-Path $root $d
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

Write-Host ""
Write-Host "== Setup done ==" -ForegroundColor Cyan
Write-Host "1. Start services: powershell -ExecutionPolicy Bypass -File scripts\start_all.ps1"
Write-Host "2. Open App: Settings -> Server address -> http://<PC-IP>:8900"
Write-Host "3. HarmonyOS App source: app-harmony/ (open with DevEco Studio)"
Write-Host "4. Android: see docs/android.md (WebView shell, coming soon)"

# 生成 config.json（首次运行）
$cfgPath = Join-Path $PSScriptRoot '..\anshiyu-server\config.json'
$examplePath = Join-Path $PSScriptRoot '..\anshiyu-server\config.example.json'
if (-not (Test-Path $cfgPath) -and (Test-Path $examplePath)) {
  $token = -join ((48..57) + (97..122) | Get-Random -Count 24 | ForEach-Object { [char]$_ })
  $cfg = Get-Content $examplePath -Raw -Encoding UTF8
  $cfg = $cfg -replace 'change-me-to-a-random-token', $token
  [IO.File]::WriteAllText($cfgPath, $cfg, (New-Object Text.UTF8Encoding($false)))
  Write-Host "已生成 config.json，连接令牌: $token" -ForegroundColor Green
}