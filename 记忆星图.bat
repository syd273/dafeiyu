@echo off
chcp 65001>nul
setlocal
set "URL=http://localhost:8899"
set "BASE=D:\大肥鱼"

curl -s -o NUL --max-time 2 %URL% >nul 2>&1
if errorlevel 1 (
  start "" /min /d "%BASE%\milky-way-3d" "D:\Python312\python.exe" server.py
  timeout /t 3 >nul
)

tasklist /fi "imagename eq astrbot.exe" 2>nul | find /i "astrbot.exe" >nul || start "" /min /d "%BASE%\AstrBot" "D:\Python312\Scripts\astrbot.exe" run
tasklist /fi "imagename eq node.exe" 2>nul | find /i "node.exe" >nul || start "" /min /d "%BASE%\qq\napcat" cmd /c napcat.bat
start "" /min "D:\Python312\python.exe" -u "%BASE%\scripts\sync_memories.py"

start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=%URL% --user-data-dir="%LOCALAPPDATA%\DafeiyuStarmap" --no-first-run --window-size=1680,1000
exit /b 0