@echo off
cd /d D:\大肥鱼\AstrBot
start "" /min D:\Python312\Scripts\astrbot.exe run
timeout /t 15 >nul
cd /d D:\大肥鱼\qq\napcat
start "" /min cmd /c "napcat.bat"
cd /d D:\大肥鱼\milky-way-3d
start "" /min D:\Python312\python.exe server.py
start "" /min D:\Python312\python.exe -u D:\大肥鱼\scripts\sync_memories.py