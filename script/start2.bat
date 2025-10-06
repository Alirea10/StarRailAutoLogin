@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "project_dir=%~dp0.."
for %%i in ("!project_dir!") do set "project_dir=%%~fi"
echo 项目根目录: !project_dir!
call "!project_dir!\.venv\Scripts\activate"
cd !project_dir!
python Login.py 2
pause