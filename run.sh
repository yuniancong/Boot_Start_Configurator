#!/bin/bash
# 开机启动管理器 - 启动脚本
# Boot Startup Manager - Launch Script

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 启动开机启动管理器..."
echo "📂 项目目录: $SCRIPT_DIR"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.6 或更高版本"
    echo ""
    echo "macOS 安装方法:"
    echo "  brew install python3"
    echo ""
    echo "Linux 安装方法:"
    echo "  sudo apt-get install python3  # Ubuntu/Debian"
    echo "  sudo yum install python3       # CentOS/RHEL"
    exit 1
fi

# 显示 Python 版本
PYTHON_VERSION=$(python3 --version)
echo "✅ 找到 $PYTHON_VERSION"
echo ""

# 检查 tkinter 是否可用
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "⚠️  警告: tkinter 未安装"
    echo ""
    echo "macOS: tkinter 通常已包含在 Python 中"
    echo "Linux 安装方法:"
    echo "  sudo apt-get install python3-tk  # Ubuntu/Debian"
    echo "  sudo yum install python3-tkinter  # CentOS/RHEL"
    echo ""
    read -p "是否继续尝试运行? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 运行主程序
cd "$SCRIPT_DIR"
python3 startup_manager.py

# 检查退出状态
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 程序正常退出"
else
    echo ""
    echo "❌ 程序异常退出"
    read -p "按回车键关闭..."
fi
