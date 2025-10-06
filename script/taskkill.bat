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

:: 直接终止已知的进程名
echo [%TIMESTAMP%] 终止 Starward 进程...
taskkill /F /IM "Starward.exe" /T >nul 2>&1

echo [%TIMESTAMP%] 终止星穹铁道进程...
taskkill /F /IM "StarRail.exe" /T >nul 2>&1

echo [%TIMESTAMP%] 终止崩坏星穹铁道启动器进程...
taskkill /F /IM "launcher.exe" /T >nul 2>&1

:: 使用 wmic 查找包含特定命令行参数的进程（更可靠）
echo [%TIMESTAMP%] 搜索其他相关进程...
for /f "tokens=2" %%p in ('wmic process where "CommandLine like '%%StarRail%%' or CommandLine like '%%Honkai%%'" get ProcessId 2^>nul ^| findstr /r "^[0-9]"') do (
    echo [%TIMESTAMP%] 终止进程 PID: %%p
    taskkill /F /PID %%p /T >nul 2>&1
)

echo.
echo [%TIMESTAMP%] 进程终止完成
echo.
pause