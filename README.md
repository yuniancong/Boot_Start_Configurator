# 🚀 开机启动管理器 (Boot Startup Manager)

一个简洁优雅的 **macOS 应用批量启动管理工具**，采用 Web 界面，让你轻松配置和管理需要启动的应用列表。

**核心功能：** 方便你在开机后通过一键脚本批量启动常用应用，避免手动一个个打开。可以自由添加、删除和调整启动顺序。

## ✨ 功能特性

- 🌐 **Web 界面** - 现代化的浏览器界面，操作直观
- 📋 **可视化管理** - 拖拽、添加、删除启动项
- 🔍 **智能搜索** - 自动扫描 macOS 已安装应用
- ➕ **灵活添加** - 从列表选择或手动输入
- 💾 **自动保存** - 配置自动持久化
- 📜 **脚本生成** - 一键生成启动脚本
- 🚀 **立即执行** - 无需重启，立即测试
- 🔄 **恢复默认** - 一键恢复完美配置

## 📦 系统要求

- **系统**: macOS 10.12 或更高版本
- **Python**: Python 3.6+
- **浏览器**: 现代浏览器（Chrome、Safari、Firefox等）

## 🚀 快速开始

### 一键启动（推荐）

```bash
./start.sh
```

就这么简单！脚本会自动：
- ✅ 检查并创建 Python 虚拟环境
- ✅ 激活虚拟环境
- ✅ 安装所需依赖（Flask）
- ✅ 启动 Web 服务器
- ✅ 自动打开浏览器

### 手动启动

如果你更喜欢手动控制：

```bash
# 1. 创建虚拟环境（首次）
python3 -m venv myenv

# 2. 激活虚拟环境
source myenv/bin/activate

# 3. 安装依赖（首次）
pip install -r requirements.txt

# 4. 启动应用
python3 app.py

# 5. 打开浏览器访问
open http://127.0.0.1:5000
```

## 📖 使用说明

### 典型使用场景

1. **配置阶段**（首次或需要调整时）：
   - 运行 `./start.sh` 打开 Web 管理界面
   - 添加/删除/调整你的常用应用
   - 点击"💾 保存配置"
   - 点击"📜 生成启动脚本"

2. **日常使用**（开机后）：
   - 直接运行 `~/startup_apps.sh`
   - 或在 Web 界面点击"🚀 立即启动应用"
   - 所有配置的应用会批量启动

### 1. 启动管理界面

运行 `./start.sh`，浏览器会自动打开管理界面。

### 2. 管理启动项

**添加应用：**
- 在右侧搜索框搜索应用
- 点击应用右侧的"➕ 添加"按钮
- 或点击"📝 手动添加"直接输入应用名

**删除应用：**
- 在左侧列表找到要删除的应用
- 点击"🗑️"删除按钮

**调整顺序：**
- 使用"↑"和"↓"按钮调整启动顺序

### 3. 保存和执行

**保存配置：**
- 点击"💾 保存配置"保存当前设置

**生成脚本：**
- 点击"📜 生成启动脚本"
- 脚本保存在 `~/startup_apps.sh`

**立即启动：**
- 点击"🚀 立即启动应用"
- 查看实时执行日志

### 4. 设置开机自启动（可选）

**注意：** 大多数情况下，你只需要在开机后手动运行 `~/startup_apps.sh` 即可。以下方法适用于希望完全自动化的用户。

#### 方法 A: 使用 Automator（推荐）

1. 打开 **Automator**
2. 创建新文稿 → 选择 **"应用程序"**
3. 添加 **"运行 Shell 脚本"** 操作
4. 输入：`~/startup_apps.sh`
5. 保存为 "启动管理器.app"
6. **系统偏好设置** → **用户与群组** → **登录项**
7. 点击 **"+"** 添加刚才保存的应用

#### 方法 B: 使用 LaunchAgent

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

## 🎯 默认应用列表

预装了 20 个常用 macOS 应用：

| 应用 | 说明 | 应用 | 说明 |
|------|------|------|------|
| Antinote | 笔记工具 | BetterTouchTool | 触控板增强 |
| Bob | 翻译工具 | CleanShot X | 截图工具 |
| Clicknow | 点击增强 | Dropover | 拖放工具 |
| Hookmark | 链接管理 | Magnet | 窗口管理 |
| Mouseless | 鼠标替代 | One Switch | 快捷开关 |
| PixelSnap | 像素测量 | PopClip | 文本增强 |
| Raycast | 启动器 | Screen Studio | 屏幕录制 |
| Shottr | 截图工具 | Snipaste | 截图工具 |
| superwhisper | 语音工具 | Surge | 网络工具 |
| Swish | 手势控制 | Voicenotes | 语音笔记 |

## 📁 项目结构

```
Boot_Start_Configurator/
├── app.py                          # Flask 后端
├── start.sh                        # 一键启动脚本
├── requirements.txt                # Python 依赖
├── templates/
│   └── index.html                  # Web 前端
├── static/
│   ├── css/
│   │   └── style.css              # 样式文件
│   └── js/
│       └── app.js                  # 前端逻辑
├── myenv/                          # Python 虚拟环境（自动创建）
├── ~/.startup_manager_config.json # 配置文件（自动创建）
└── ~/startup_apps.sh              # 生成的启动脚本（自动创建）
```

## 🔧 高级用法

### 配置文件格式

配置文件 `~/.startup_manager_config.json`:

```json
{
  "apps": [
    "Raycast",
    "BetterTouchTool",
    "Magnet"
  ]
}
```

### 自定义端口

编辑 `app.py` 最后一行：

```python
app.run(host='127.0.0.1', port=5000, debug=True)
```

将 `port=5000` 改为你想要的端口。

### 启动脚本说明

生成的脚本采用**经过实际试错验证的完美版本逻辑**，确保百分之百启动成功：

- ✅ 智能检测应用是否已运行，避免重复启动
- 🔄 自动激活应用确保菜单栏/辅助功能类 App 初始化成功
- 🙈 尝试隐藏窗口，保持桌面整洁（需辅助功能权限）
- ⏱️ 启动间隔 0.8 秒，避免系统负载过高
- 📝 详细的启动日志输出
- ⚠️ 错误处理：应用不存在时给出提示，不中断执行

**脚本格式完全遵循试错过的完美版本**，可靠稳定。

### 辅助功能权限

某些功能需要授予辅助功能权限：

1. **系统偏好设置** → **安全性与隐私** → **隐私** → **辅助功能**
2. 添加 **"终端"** 或你使用的终端应用

## ❓ 常见问题

### Q: 如何停止服务器？

A: 在运行 `start.sh` 的终端按 `Ctrl+C`。

### Q: 端口被占用怎么办？

A: 启动脚本会自动处理。或手动终止：
```bash
lsof -ti:5000 | xargs kill -9
```

### Q: 虚拟环境在哪里？

A: 在项目目录的 `myenv/` 文件夹。首次运行时自动创建。

### Q: 如何重置配置？

A: 删除配置文件：
```bash
rm ~/.startup_manager_config.json
```

### Q: 应用启动失败？

A: 检查：
1. 应用名称是否正确
2. 应用是否安装在 `/Applications` 或 `~/Applications`
3. 查看日志输出的错误信息

### Q: 如何卸载？

A:
```bash
# 停止 LaunchAgent（如果设置了）
launchctl unload ~/Library/LaunchAgents/com.startup.manager.plist
rm ~/Library/LaunchAgents/com.startup.manager.plist

# 删除配置和脚本
rm ~/.startup_manager_config.json
rm ~/startup_apps.sh

# 删除项目目录
rm -rf /path/to/Boot_Start_Configurator
```

## 🛠️ 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5 + CSS3 + JavaScript
- **样式**: 现代渐变 UI
- **存储**: JSON 配置文件

## 📝 注意事项

- 本应用仅支持 macOS
- 需要 Python 3.6 或更高版本
- 首次运行会自动安装依赖
- 配置文件保存在用户目录
- Web 服务器仅监听本地（127.0.0.1）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**Made with ❤️ for macOS users**

**Enjoy effortless app management! 🎉**
