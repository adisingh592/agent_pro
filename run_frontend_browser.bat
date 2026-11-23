@echo off
title Personal Agent - Futuristic Control Center
cd /d "%~dp0"
echo Starting Personal Agent on http://localhost:1420/ ...
start http://localhost:1420/
npm run dev
