#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import ctypes
import subprocess
import time
from datetime import datetime


def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """请求管理员权限重新运行脚本"""
    if sys.platform != 'win32':
        print("此脚本仅支持 Windows 系统")
        return False

    print("需要管理员权限来终止进程...")
    print('请在弹出的UAC窗口中点击"是"...')

    try:
        # 使用 ShellExecute 请求管理员权限
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            f'"{script}" {params}',
            None,
            1
        )
        return True
    except Exception as e:
        print(f"请求管理员权限失败: {e}")
        return False


def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def kill_process_by_name(process_name):
    """通过进程名终止进程"""
    timestamp = get_timestamp()
    print(f"[{timestamp}] 终止 {process_name} 进程...")

    try:
        # 使用 taskkill 命令强制终止进程
        subprocess.run(
            ['taskkill', '/F', '/IM', process_name, '/T'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            encoding='utf-8',
            errors='ignore'
        )
    except Exception as e:
        print(f"[{timestamp}] 终止进程时出错: {e}")


def kill_process_by_pid(pid):
    """通过PID终止进程"""
    timestamp = get_timestamp()
    print(f"[{timestamp}] 终止进程 PID: {pid}")

    try:
        subprocess.run(
            ['taskkill', '/F', '/PID', str(pid), '/T'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            encoding='utf-8',
            errors='ignore'
        )
    except Exception as e:
        print(f"[{timestamp}] 终止进程时出错: {e}")


def find_processes_by_commandline(keywords):
    """通过命令行参数查找进程"""
    timestamp = get_timestamp()
    print(f"[{timestamp}] 搜索其他相关进程...")

    try:
        # 使用 PowerShell 查询进程，设置输出编码为 UTF-8
        ps_command = (
            f'[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
            f'Get-Process | Where-Object {{$_.Path -like "*{keywords[0]}*" -or $_.Path -like "*{keywords[1]}*"}} | '
            f'Select-Object -ExpandProperty Id'
        )

        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', ps_command],
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='ignore'
        )

        # 解析输出获取 PID
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and line.isdigit():
                    kill_process_by_pid(line)
        else:
            # 如果 PowerShell 方法失败，尝试使用 tasklist
            try_tasklist_method(keywords)

    except Exception as e:
        print(f"[{timestamp}] 搜索进程时出错: {e}")
        # 尝试备用方法
        try_tasklist_method(keywords)


def try_tasklist_method(keywords):
    """使用 tasklist 作为备用方法"""
    try:
        # 使用 chcp 65001 强制切换到 UTF-8，然后执行 tasklist
        result = subprocess.run(
            ['cmd', '/c', 'chcp 65001 >nul && tasklist /V /FO CSV'],
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='ignore'
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # 跳过标题行
                # 检查是否包含关键词
                if any(keyword.lower() in line.lower() for keyword in keywords):
                    # 解析 CSV 格式获取 PID
                    parts = line.split('","')
                    if len(parts) > 1:
                        pid = parts[1].strip('"')
                        if pid.isdigit():
                            kill_process_by_pid(pid)
    except Exception as e:
        timestamp = get_timestamp()
        print(f"[{timestamp}] tasklist 方法也失败: {e}")


def main():
    """主函数"""
    # 检查管理员权限
    if not is_admin():
        # 请求管理员权限并重新运行
        if run_as_admin():
            time.sleep(3)  # 等待新进程启动
        sys.exit(0)

    # 管理员模式下的主逻辑
    timestamp = get_timestamp()
    print(f"[{timestamp}] 管理员权限已获取")
    print(f"[{timestamp}] 强力终止游戏进程...")
    print()

    # 终止已知的进程 - 使用列表统一管理
    process_list = ["Starward.exe", "StarRail.exe", "launcher.exe", "OCR.json"]
    for process_name in process_list:
        kill_process_by_name(process_name)

    # 搜索并终止包含特定关键词的进程
    find_processes_by_commandline(["StarRail", "Honkai"])

    print()
    timestamp = get_timestamp()
    print(f"[{timestamp}] 进程终止完成")
    print()

    # 等待用户按键 - 处理EOF异常
    try:
        input("按任意键退出...")
    except (EOFError, KeyboardInterrupt):
        print("程序退出")


if __name__ == "__main__":
    main()
