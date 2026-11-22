@echo off
title Personal Agent - Futuristic AI Dashboard
cd /d "%~dp0"
echo ========================================================
echo   Launching Personal Agent - Futuristic Control Deck
echo ========================================================
echo Opening Orbital Dashboard in your browser...
start http://localhost:1420/templates/orbital/overview.html
npm run dev
