@echo off
title Personal Agent - Futuristic AI Dashboard
cd /d "%~dp0"
echo Starting Personal Agent Orbital Dashboard on http://localhost:1420/templates/orbital/overview.html ...
start http://localhost:1420/templates/orbital/overview.html
npm run dev
