@echo off
title Personal Agent - Modern UI (Browser Preview)
cd /d "%~dp0"
echo Starting Personal Agent Modern Frontend on http://localhost:1420 ...
start http://localhost:1420
npm run dev
