#!/bin/bash
# 开机启动管理器 - 一键启动脚本
# Boot Startup Manager - One-Click Start Script

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 开机启动管理器 - 启动中...      ║${NC}"
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Python 3${NC}"
    echo "请先安装 Python 3.6 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Python: $PYTHON_VERSION"

# 检查虚拟环境是否存在
if [ ! -d "myenv" ]; then
    echo -e "${YELLOW}⚠ 虚拟环境不存在，正在创建...${NC}"
    python3 -m venv myenv

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} 虚拟环境创建成功"
    else
        echo -e "${RED}❌ 虚拟环境创建失败${NC}"
        exit 1
    fi
fi

# 激活虚拟环境
echo -e "${BLUE}→${NC} 激活虚拟环境..."
source myenv/bin/activate

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 激活虚拟环境失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} 虚拟环境已激活"

# 检查并安装依赖
echo -e "${BLUE}→${NC} 检查依赖..."

if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Flask 未安装，正在安装...${NC}"
    pip install flask -q

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Flask 安装成功"
    else
        echo -e "${RED}❌ Flask 安装失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Flask 已安装"
fi

# 启动 Flask 后端
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🌐 启动 Web 服务器...              ║${NC}"
echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo ""

# 检查端口是否被占用
PORT=5000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 端口 $PORT 已被占用，尝试终止占用进程...${NC}"
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# 在后台启动 Flask
python3 app.py > /dev/null 2>&1 &
FLASK_PID=$!

# 等待服务器启动
echo -e "${BLUE}→${NC} 等待服务器启动..."
sleep 2

# 检查服务器是否成功启动
if ! ps -p $FLASK_PID > /dev/null; then
    echo -e "${RED}❌ 服务器启动失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} 服务器启动成功 (PID: $FLASK_PID)"
echo ""

# 打开浏览器
URL="http://127.0.0.1:5000"
echo -e "${BLUE}→${NC} 打开浏览器: ${URL}"

# macOS 打开浏览器
open "$URL" 2>/dev/null

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ 启动完成！                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}访问地址:${NC} ${URL}"
echo -e "${BLUE}Flask PID:${NC} ${FLASK_PID}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo ""

# 等待用户中断
trap "echo -e '\n${YELLOW}正在停止服务器...${NC}'; kill $FLASK_PID 2>/dev/null; echo -e '${GREEN}✓ 服务器已停止${NC}'; exit 0" INT TERM

# 保持脚本运行
wait $FLASK_PID
