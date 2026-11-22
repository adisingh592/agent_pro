@echo off
title Personal Agent - Orbit Environment
cd /d "%~dp0"
echo ========================================================
echo   Launching Personal Agent - Orbit Intelligent UI
echo ========================================================
echo Opening http://localhost:1420 in browser...
start http://localhost:1420
npm run dev
