@echo off
REM 开机启动管理器 - 启动脚本 (Windows)
REM Boot Startup Manager - Launch Script (Windows)

chcp 65001 >nul
title 开机启动管理器

echo.
echo 🚀 启动开机启动管理器...
echo 📂 项目目录: %~dp0
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python
    echo.
    echo 请先安装 Python 3.6 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 显示 Python 版本
echo ✅ 找到 Python:
python --version
echo.

REM 运行主程序
cd /d "%~dp0"
python startup_manager.py

REM 检查退出状态
if %errorlevel% equ 0 (
    echo.
    echo ✅ 程序正常退出
) else (
    echo.
    echo ❌ 程序异常退出
    pause
)
