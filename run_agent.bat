@echo off
title Personal Agent - Futuristic Control Center
cd /d "%~dp0"
echo ========================================================
echo   Launching Personal Agent - Control Center
echo ========================================================
echo Opening Personal Agent Main Hub in your browser...
start http://localhost:1420/
npm run dev
