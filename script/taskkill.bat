@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 检查重启标志
if "%~1"=="admin" (
    goto :admin_mode
)

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% equ 0 (
    goto :admin_mode
)

:: 不是管理员，请求提权
echo 需要管理员权限来终止进程...
echo 请在弹出的UAC窗口中点击"是"...

:: 使用VBScript来更可靠地提权
set "batchPath=%~f0"
echo Set UAC = CreateObject("Shell.Application") > "%temp%\elevate.vbs"
echo UAC.ShellExecute "cmd.exe", "/c ""%batchPath% admin""", "", "runas", 1 >> "%temp%\elevate.vbs"

"%temp%\elevate.vbs"
timeout /t 3 /nobreak >nul
del "%temp%\elevate.vbs" >nul 2>&1
exit /b

:admin_mode
:: 管理员模式下的主逻辑

:: 获取时间
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do set "mdate=%%a/%%b/%%c"
for /f "tokens=1-3 delims=:." %%a in ('echo %time%') do set "mtime=%%a:%%b:%%c"
set "TIMESTAMP=%mdate% %mtime%"

echo [%TIMESTAMP%] 管理员权限已获取
echo [%TIMESTAMP%] 强力终止游戏进程...
echo.

set "keywords=Starward 崩坏：星穹铁道 Honkai StarRail OCR.json"

for %%k in (%keywords%) do (
    echo [%TIMESTAMP%] 搜索包含 "%%k" 的进程...

    for /f "tokens=1,2 delims=:" %%a in ('powershell -Command "Get-Process *%%k* -ErrorAction SilentlyContinue | ForEach-Object { $_.Name + ':' + $_.Id }" 2^>nul') do (
        if not "%%b"=="" (
            echo [%TIMESTAMP%] 终止: %%a (PID: %%b)
            taskkill /F /PID %%b /T >nul 2>&1
        )
    )
)

echo.
echo [%TIMESTAMP%] 进程终止完成
echo.
pause