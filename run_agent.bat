@echo off
title Personal Agent - Aurora Control Center
cd /d "%~dp0"
echo ========================================================
echo   Launching Personal Agent Aurora - Control Center
echo ========================================================
echo Opening Personal Agent Aurora in your browser...
start http://localhost:1420/templates/aurora/overview.html
npm run dev
