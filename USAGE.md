# 📚 使用指南 (Usage Guide)

## 🎬 快速演示

### 第一步：启动程序

```bash
# macOS / Linux
./run.sh

# Windows
run.bat

# 或直接使用 Python
python3 startup_manager.py
```

### 第二步：配置启动项

#### 场景 1: 使用默认配置

如果你是 macOS 用户，程序已经预装了 20 个常用应用的配置，直接点击"🚀 立即启动应用"即可。

#### 场景 2: 自定义配置

1. **删除不需要的应用**
   - 在左侧列表选中应用
   - 点击"🗑️ 删除"

2. **添加新应用**

   **方法 A: 从列表选择**
   - 在右侧搜索框输入应用名称（如 "Chrome"）
   - 从过滤后的列表选择应用
   - 点击"➕ 添加选中"

   **方法 B: 手动输入**
   - 点击"📝 手动输入"
   - 输入应用名称
   - 点击"添加"

3. **调整启动顺序**
   - 选中应用
   - 使用"↑ 上移"或"↓ 下移"调整位置

4. **保存配置**
   - 点击"💾 保存配置"

### 第三步：使用启动脚本

#### 选项 A: 立即测试

点击"🚀 立即启动应用"，程序会：
1. 自动生成启动脚本
2. 执行脚本启动所有应用
3. 显示实时日志

#### 选项 B: 手动执行脚本

```bash
# macOS / Linux
bash ~/startup_apps.sh

# Windows
%USERPROFILE%\startup_apps.bat
```

#### 选项 C: 设置开机自启动

参见 [README.md](README.md) 的"设置开机自启动"部分。

## 🔍 功能详解

### 应用扫描机制

程序会自动扫描以下位置：

**macOS:**
- `/Applications` - 系统应用
- `~/Applications` - 用户应用

**Windows:**
- `C:\Program Files`
- `C:\Program Files (x86)`
- `%LOCALAPPDATA%\Programs`

**Linux:**
- `/usr/share/applications`
- `~/.local/share/applications`

### 搜索功能

- **实时搜索**: 输入即搜索，无需按回车
- **模糊匹配**: 支持部分匹配（如输入"chro"可以找到"Chrome"）
- **大小写不敏感**: 搜索时忽略大小写

### 配置文件

配置文件保存在 `~/.startup_manager_config.json`：

```json
{
  "apps": [
    "Raycast",
    "BetterTouchTool",
    "Magnet"
  ]
}
```

你可以：
- 手动编辑此文件
- 复制到其他电脑使用
- 版本控制管理

### 启动脚本特性 (macOS)

生成的脚本会：

1. **检查应用是否已运行**
   - 避免重复启动
   - 显示"✅ 已在运行"

2. **智能启动**
   - 启动未运行的应用
   - 自动激活确保初始化
   - 尝试隐藏窗口（需要辅助功能权限）

3. **错误处理**
   - 如果应用不存在，显示警告
   - 不会因为单个应用失败而中断

4. **启动间隔**
   - 每个应用间隔 0.8 秒
   - 避免系统负载过高

## 💡 使用技巧

### 技巧 1: 分类管理

你可以创建多个配置用于不同场景：

```bash
# 工作配置
cp ~/.startup_manager_config.json ~/.startup_work.json

# 娱乐配置
cp ~/.startup_manager_config.json ~/.startup_entertainment.json

# 切换配置
cp ~/.startup_work.json ~/.startup_manager_config.json
```

### 技巧 2: 快速备份

```bash
# 备份当前配置
cp ~/.startup_manager_config.json ~/.startup_manager_config.backup.json

# 恢复备份
cp ~/.startup_manager_config.backup.json ~/.startup_manager_config.json
```

### 技巧 3: 延迟启动

如果某些应用启动太快会出问题，可以编辑脚本增加延迟：

```bash
# 编辑脚本
nano ~/startup_apps.sh

# 找到 sleep 0.8，改成更大的值，如：
sleep 2.0  # 延迟 2 秒
```

### 技巧 4: 条件启动

可以在脚本中添加条件，只在特定情况下启动：

```bash
# 只在工作日启动
if [ $(date +%u) -le 5 ]; then
    # 启动工作相关应用
    open -a "Slack"
fi

# 只在特定时间启动
hour=$(date +%H)
if [ $hour -ge 9 ] && [ $hour -le 18 ]; then
    # 启动工作应用
fi
```

## ⚠️ 注意事项

### macOS 权限问题

某些应用需要辅助功能权限才能正常启动和隐藏窗口：

1. 系统偏好设置 → 安全性与隐私 → 隐私 → 辅助功能
2. 添加"终端"或你使用的终端应用

### Windows 防火墙

首次运行脚本时，Windows 可能会弹出防火墙提示，选择"允许访问"。

### Linux 桌面环境

不同的 Linux 桌面环境（GNOME、KDE、XFCE等）设置自启动的方式可能略有不同。

## 🐛 故障排除

### 问题 1: 应用启动后立即关闭

**原因**: 应用可能需要参数或已经在运行

**解决方案**:
```bash
# 检查应用是否在运行
# macOS
osascript -e 'tell application "System Events" to get name of processes'

# Linux
ps aux | grep <应用名>

# Windows
tasklist | findstr <应用名>
```

### 问题 2: 某些应用无法启动

**原因**: 应用名称不正确或路径问题

**解决方案**:
```bash
# macOS - 查找正确的应用名称
ls /Applications | grep -i <部分名称>

# 手动测试启动
open -a "正确的应用名称"
```

### 问题 3: 脚本执行权限不足

**解决方案**:
```bash
# 添加执行权限
chmod +x ~/startup_apps.sh

# 检查权限
ls -l ~/startup_apps.sh
```

### 问题 4: tkinter 无法导入

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**CentOS/RHEL**:
```bash
sudo yum install python3-tkinter
```

**macOS**:
```bash
# 通常已包含，如果没有：
brew install python-tk
```

## 📞 获取帮助

如果遇到问题：

1. 查看 [README.md](README.md) 的常见问题部分
2. 检查 Python 和系统版本是否符合要求
3. 确认应用名称是否正确
4. 查看启动脚本的日志输出

---

**祝使用愉快！Happy Automating! 🎉**
