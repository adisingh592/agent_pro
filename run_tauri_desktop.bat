@echo off
title Personal Agent - Desktop Native (Tauri 2)
cd /d "%~dp0"
set "PATH=C:\Users\prtap\.cargo\bin;%PATH%"
echo Starting Personal Agent Native Desktop Window (Tauri 2)...
npm run tauri -- dev
