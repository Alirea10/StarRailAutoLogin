@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 正在检测Python环境...

REM 检测Python是否安装
echo 正在检测Python 3.11安装...

set "python_311_found="
set "python_cmd="

REM 首先尝试python3.11命令
python3.11 --version >nul 2>&1
if not errorlevel 1 (
    set "python_cmd=python3.11"
    set "python_311_found=true"
) else (
    REM 如果没有python3.11命令，检查所有python命令
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if not defined python_311_found (
            "%%i" --version 2>&1 | findstr /r /c:"3\.11\." >nul
            if not errorlevel 1 (
                set "python_cmd=%%i"
                set "python_311_found=true"
            )
        )
    )
)

REM 检查是否找到Python 3.11
if not defined python_311_found (
    echo 错误：未检测到Python 3.11.x版本
    echo 请安装Python 3.11.x或确保其在PATH中
    echo.
    echo 当前检测到的Python版本：
    python --version 2>&1
    where python 2>nul
    pause
    exit /b 1
)

REM 获取Python版本
for /f "tokens=*" %%i in ('"!python_cmd!" --version 2^>^&1') do set "python_version=%%i"
echo 检测到Python 3.11版本: !python_version!
echo 使用的Python路径: !python_cmd!

REM 获取批处理文件所在目录并转到上一级目录
set "bat_dir=%~dp0"
echo 批处理文件所在目录: !bat_dir!

REM 正确获取上一级目录（项目根目录）
set "project_dir=%~dp0.."
for %%i in ("!project_dir!") do set "project_dir=%%~fi"
echo 项目根目录: !project_dir!

REM 检查requirements.txt文件是否存在
set "requirements_file=!project_dir!\requirements.txt"
if not exist "!requirements_file!" (
    echo 错误：未找到requirements.txt文件
    echo 请确保在项目根目录!project_dir!存在requirements.txt文件
    pause
    exit /b 1
)

REM 检查虚拟环境是否已存在
if exist "!project_dir!\.venv\" (
    echo 虚拟环境已存在: !project_dir!\.venv
    echo 跳过虚拟环境创建
    call "!project_dir!\.venv\Scripts\activate.bat"
    if errorlevel 1 (
        echo 错误：激活虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境已激活

    REM 即使虚拟环境已存在，也继续安装依赖
    echo.
    echo 检查并安装依赖包...
    REM 如果安装不了，可能是网络问题，可以给下方指令加上 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    REM 但是镜像源不一定包含所有包，可能会导致部分包安装失败，所以默认不使用镜像源
    pip install -r "!requirements_file!"
    if errorlevel 1 (
        echo 警告：部分依赖包安装可能失败
    ) else (
        echo 所有依赖包安装完成
    )

    echo 当前环境信息：
    python --version
    echo 已安装的依赖包列表:
    pip list
    pause
    exit /b 0
)



REM 创建虚拟环境
echo 正在创建虚拟环境...
python -m venv "!project_dir!\.venv"
if errorlevel 1 (
    echo 错误：创建虚拟环境失败
    pause
    exit /b 1
)
echo 虚拟环境已创建在: !project_dir!\.venv

REM 激活虚拟环境
echo 正在激活虚拟环境...
call "!project_dir!\.venv\Scripts\activate"
if errorlevel 1 (
    echo 错误：激活虚拟环境失败
    pause
    exit /b 1
)
echo 虚拟环境已激活

REM 安装requirements.txt中的依赖
echo 正在安装依赖包...
pip install -r "!requirements_file!" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if errorlevel 1 (
    echo 警告：部分依赖包安装可能失败
) else (
    echo 所有依赖包安装完成
)

echo.
echo 环境设置完成！
echo.
echo Python版本: !python_version!
echo.
echo 虚拟环境位置: !project_dir!\.venv
echo.
echo 已安装的依赖包列表:
pip list

pause