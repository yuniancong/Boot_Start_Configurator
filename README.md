# 🚀 开机启动管理器 (Boot Startup Manager)

一个功能强大的可视化开机启动管理工具，支持 macOS、Windows 和 Linux 系统。

## ✨ 功能特性

- 📋 **可视化管理** - 直观的图形界面管理启动项
- 🔍 **智能搜索** - 自动扫描本地已安装应用，支持搜索过滤
- ➕ **灵活添加** - 支持从列表选择或手动输入应用名称
- 🗑️ **快速删除** - 一键删除不需要的启动项
- ⬆️⬇️ **调整顺序** - 自由调整应用启动顺序
- 💾 **配置保存** - 自动保存配置，下次打开即可使用
- 📜 **脚本生成** - 自动生成适合当前系统的启动脚本
- 🚀 **立即启动** - 无需重启，立即执行启动流程
- 🔄 **恢复默认** - 一键恢复到完美版本配置

## 📦 安装要求

### Python 环境
- Python 3.6 或更高版本
- tkinter (通常Python自带)

### 系统要求
- **macOS**: 10.12 或更高版本
- **Windows**: Windows 7 或更高版本
- **Linux**: 任何支持 GUI 的发行版

## 🚀 快速开始

### 方法 1: 直接运行 Python 程序

```bash
# 进入项目目录
cd Boot_Start_Configurator

# 运行程序
python3 startup_manager.py
```

### 方法 2: 使用启动脚本 (macOS/Linux)

```bash
# 给脚本添加执行权限
chmod +x run.sh

# 运行
./run.sh
```

### 方法 3: Windows 用户

```cmd
# 双击运行
run.bat
```

## 📖 使用说明

### 1️⃣ 初次启动

程序启动后会自动：
- 加载默认的完美版本配置（包含20个常用macOS应用）
- 扫描系统已安装的应用程序
- 创建配置文件 `~/.startup_manager_config.json`

### 2️⃣ 管理启动项

**添加应用：**
- 🔍 在右侧搜索框输入应用名称进行过滤
- 📝 从列表选择应用后点击"➕ 添加选中"
- ✏️ 或点击"📝 手动输入"直接输入应用名称

**删除应用：**
- 在左侧列表选中要删除的应用
- 点击"🗑️ 删除"按钮

**调整顺序：**
- 选中应用后使用"↑ 上移"或"↓ 下移"按钮调整启动顺序

### 3️⃣ 保存和使用配置

**保存配置：**
- 点击"💾 保存配置"将当前启动列表保存到配置文件
- 配置文件位置：`~/.startup_manager_config.json`

**生成启动脚本：**
- 点击"📜 生成启动脚本"创建可执行的启动脚本
- 脚本位置：`~/startup_apps.sh` (macOS/Linux) 或 `~/startup_apps.bat` (Windows)

**立即启动：**
- 点击"🚀 立即启动应用"会自动生成并执行启动脚本
- 弹出窗口实时显示启动日志

**恢复默认：**
- 点击"🔄 恢复默认"可以恢复到完美版本的配置

### 4️⃣ 设置开机自启动

#### macOS 方法

**方法 A: 使用 Automator (推荐)**

1. 打开 Automator
2. 创建新文稿 → 选择"应用程序"
3. 添加"运行 Shell 脚本"操作
4. 输入：`~/startup_apps.sh`
5. 保存为"启动管理器.app"
6. 系统偏好设置 → 用户与群组 → 登录项 → 添加此应用

**方法 B: 使用 LaunchAgent**

```bash
# 创建 plist 文件
cat > ~/Library/LaunchAgents/com.startup.manager.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.startup.manager</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>$HOME/startup_apps.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加载服务
launchctl load ~/Library/LaunchAgents/com.startup.manager.plist
```

#### Windows 方法

1. 按 `Win + R` 打开运行
2. 输入 `shell:startup` 打开启动文件夹
3. 创建快捷方式指向 `%USERPROFILE%\startup_apps.bat`

#### Linux 方法

**方法 A: 使用桌面环境的自启动设置**

1. 打开系统设置 → 启动应用程序
2. 添加命令：`/bin/bash ~/startup_apps.sh`

**方法 B: 编辑 .bashrc 或 .profile**

```bash
echo '~/startup_apps.sh &' >> ~/.bashrc
```

## 🎯 默认应用列表

完美版本包含以下 macOS 应用：

1. Antinote - 笔记工具
2. BetterTouchTool - 触控板增强
3. Bob - 翻译工具
4. CleanShot X - 截图工具
5. Clicknow - 点击增强
6. Dropover - 拖放工具
7. Hookmark - 链接管理
8. Magnet - 窗口管理
9. Mouseless - 鼠标替代
10. One Switch - 快捷开关
11. PixelSnap - 像素测量
12. PopClip - 文本选择增强
13. Raycast - 启动器
14. Screen Studio - 屏幕录制
15. Shottr - 截图工具
16. Snipaste - 截图工具
17. superwhisper - 语音工具
18. Surge - 网络工具
19. Swish - 手势控制
20. Voicenotes - 语音笔记

## 📁 文件说明

```
Boot_Start_Configurator/
├── startup_manager.py          # 主程序
├── run.sh                      # macOS/Linux 启动脚本
├── run.bat                     # Windows 启动脚本
├── README.md                   # 本文档
├── 可参照完美版本启动脚本.txt # 原始脚本参考
└── ~/.startup_manager_config.json  # 配置文件（自动生成）
└── ~/startup_apps.sh          # 生成的启动脚本（自动生成）
```

## 🔧 高级功能

### 配置文件格式

配置文件 `~/.startup_manager_config.json` 采用 JSON 格式：

```json
{
  "apps": [
    "Raycast",
    "BetterTouchTool",
    "Magnet",
    ...
  ]
}
```

您也可以手动编辑此文件来批量修改启动项。

### 启动脚本说明

生成的 macOS 启动脚本具有以下特性：
- ✅ 检查应用是否已运行，避免重复启动
- 🔄 自动激活应用确保初始化成功
- 🙈 自动隐藏窗口（如果有辅助功能权限）
- ⏱️ 启动间隔 0.8 秒，避免系统负载过大
- 📝 详细的启动日志输出

## ❓ 常见问题

### Q: 程序无法启动？
A: 确保安装了 Python 3.6+ 和 tkinter。macOS 可通过 `python3 --version` 检查。

### Q: 扫描不到已安装的应用？
A: 点击"🔄 刷新"按钮重新扫描，或使用"📝 手动输入"功能添加。

### Q: macOS 提示"无法打开应用"？
A: 需要给应用授予"辅助功能"权限：系统偏好设置 → 安全性与隐私 → 辅助功能。

### Q: 某些应用启动后立即退出？
A: 可能是应用需要特定参数或权限，建议查看该应用的官方文档。

### Q: 如何设置启动延迟？
A: 在生成的脚本中，每个应用之间有 0.8 秒延迟，可手动编辑脚本中的 `sleep 0.8` 调整。

### Q: Windows 下应用路径包含空格怎么办？
A: 程序会自动处理路径中的空格，无需特殊处理。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 鸣谢

基于原始的完美版本启动脚本开发，感谢原作者的创意！

---

**Made with ❤️ for better productivity**
