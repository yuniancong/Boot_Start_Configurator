#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开机启动管理器 - Flask 后端
Boot Startup Manager - Flask Backend (macOS Only)
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
from pathlib import Path

app = Flask(__name__)

# 配置文件路径
CONFIG_FILE = Path.home() / ".startup_manager_config.json"
# 默认脚本路径改为桌面
DEFAULT_SCRIPT_FILE = Path.home() / "Desktop" / "startup_apps.sh"

# 默认应用列表
DEFAULT_APPS = [
    "Antinote", "BetterTouchTool", "Bob", "CleanShot X", "Clicknow",
    "Dropover", "Hookmark", "Magnet", "Mouseless", "One Switch",
    "PixelSnap", "PopClip", "Raycast", "Screen Studio", "Shottr",
    "Snipaste", "superwhisper", "Surge", "Swish", "Voicenotes"
]


@app.route('/')
def index():
    """主页"""
    # 传递默认脚本路径给前端
    return render_template('index.html', default_script_path=str(DEFAULT_SCRIPT_FILE))


@app.route('/api/apps', methods=['GET'])
def get_apps():
    """获取当前启动项列表"""
    apps = load_config()
    return jsonify({"apps": apps})


@app.route('/api/apps', methods=['POST'])
def save_apps():
    """保存启动项列表"""
    data = request.get_json()
    apps = data.get('apps', [])

    if save_config(apps):
        return jsonify({"success": True, "message": "保存成功"})
    else:
        return jsonify({"success": False, "message": "保存失败"}), 500


@app.route('/api/apps/add', methods=['POST'])
def add_app():
    """添加应用"""
    data = request.get_json()
    app_name = data.get('name', '').strip()

    if not app_name:
        return jsonify({"success": False, "message": "应用名称不能为空"}), 400

    apps = load_config()

    if app_name in apps:
        return jsonify({"success": False, "message": "应用已存在"}), 400

    apps.append(app_name)

    if save_config(apps):
        return jsonify({"success": True, "message": f"已添加 {app_name}", "apps": apps})
    else:
        return jsonify({"success": False, "message": "保存失败"}), 500


@app.route('/api/apps/remove', methods=['POST'])
def remove_app():
    """删除应用"""
    data = request.get_json()
    index = data.get('index')

    if index is None:
        return jsonify({"success": False, "message": "缺少索引"}), 400

    apps = load_config()

    if index < 0 or index >= len(apps):
        return jsonify({"success": False, "message": "索引无效"}), 400

    removed = apps.pop(index)

    if save_config(apps):
        return jsonify({"success": True, "message": f"已删除 {removed}", "apps": apps})
    else:
        return jsonify({"success": False, "message": "保存失败"}), 500


@app.route('/api/apps/move', methods=['POST'])
def move_app():
    """移动应用位置"""
    data = request.get_json()
    from_index = data.get('from')
    to_index = data.get('to')

    if from_index is None or to_index is None:
        return jsonify({"success": False, "message": "缺少索引"}), 400

    apps = load_config()

    if from_index < 0 or from_index >= len(apps) or to_index < 0 or to_index >= len(apps):
        return jsonify({"success": False, "message": "索引无效"}), 400

    app = apps.pop(from_index)
    apps.insert(to_index, app)

    if save_config(apps):
        return jsonify({"success": True, "apps": apps})
    else:
        return jsonify({"success": False, "message": "保存失败"}), 500


@app.route('/api/apps/restore', methods=['POST'])
def restore_defaults():
    """恢复默认配置"""
    if save_config(DEFAULT_APPS.copy()):
        return jsonify({"success": True, "message": "已恢复默认配置", "apps": DEFAULT_APPS})
    else:
        return jsonify({"success": False, "message": "恢复失败"}), 500


@app.route('/api/installed', methods=['GET'])
def get_installed_apps():
    """获取已安装的应用列表"""
    apps = scan_installed_apps()
    return jsonify({"apps": apps})


@app.route('/api/script/content', methods=['GET'])
def get_script_content():
    """获取脚本内容（用于复制）"""
    apps = load_config()

    if not apps:
        return jsonify({"success": False, "message": "启动列表为空"}), 400

    script_content = generate_startup_script(apps)

    return jsonify({
        "success": True,
        "content": script_content
    })


@app.route('/api/script/generate', methods=['POST'])
def generate_script():
    """生成启动脚本"""
    data = request.get_json() or {}
    custom_path = data.get('path', '')

    apps = load_config()

    if not apps:
        return jsonify({"success": False, "message": "启动列表为空"}), 400

    # 如果指定了自定义路径，使用自定义路径，否则使用默认桌面路径
    if custom_path:
        script_file = Path(custom_path).expanduser()
    else:
        script_file = DEFAULT_SCRIPT_FILE

    script_content = generate_startup_script(apps)

    try:
        # 确保目录存在
        script_file.parent.mkdir(parents=True, exist_ok=True)

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 设置可执行权限
        os.chmod(script_file, 0o755)

        return jsonify({
            "success": True,
            "message": f"脚本已生成",
            "path": str(script_file)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"生成失败：{str(e)}"}), 500


@app.route('/api/script/run', methods=['POST'])
def run_script():
    """执行启动脚本"""
    data = request.get_json() or {}
    custom_path = data.get('path', '')

    apps = load_config()

    if not apps:
        return jsonify({"success": False, "message": "启动列表为空"}), 400

    # 如果指定了自定义路径，使用自定义路径，否则使用默认桌面路径
    if custom_path:
        script_file = Path(custom_path).expanduser()
    else:
        script_file = DEFAULT_SCRIPT_FILE

    script_content = generate_startup_script(apps)

    try:
        # 确保目录存在
        script_file.parent.mkdir(parents=True, exist_ok=True)

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        os.chmod(script_file, 0o755)

        # 执行脚本
        result = subprocess.run(
            ['/bin/bash', str(script_file)],
            capture_output=True,
            text=True,
            timeout=60
        )

        return jsonify({
            "success": True,
            "message": "执行完成",
            "output": result.stdout + result.stderr,
            "path": str(script_file)
        })
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "message": "执行超时"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"执行失败：{str(e)}"}), 500


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('apps', DEFAULT_APPS.copy())
        except Exception as e:
            print(f"加载配置失败：{e}")
            return DEFAULT_APPS.copy()
    else:
        return DEFAULT_APPS.copy()


def save_config(apps):
    """保存配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"apps": apps}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置失败：{e}")
        return False


def scan_installed_apps():
    """扫描已安装的应用"""
    apps = []
    app_dirs = ["/Applications", str(Path.home() / "Applications")]

    for app_dir in app_dirs:
        if os.path.exists(app_dir):
            try:
                for item in os.listdir(app_dir):
                    if item.endswith('.app'):
                        app_name = item.replace('.app', '')
                        if app_name not in apps:
                            apps.append(app_name)
            except PermissionError:
                continue

    apps.sort()
    return apps


def generate_startup_script(apps):
    """生成启动脚本 - 完全按照完美版本的格式"""
    apps_array = '\n'.join([f'"{app}"' for app in apps])

    return f'''#!/bin/bash
# 一键启动：仅启动未在运行的这些 App（已运行的跳过）
apps=(
{apps_array}
)

echo "🚀 检查并启动应用（已运行的将跳过）..."
for name in "${{apps[@]}}"; do
  # 判断是否运行
  if osascript -e 'tell application "System Events" to return (name of processes) contains "'"$name"'"' 2>/dev/null | grep -qi true; then
    echo "✅ 已在运行：$name"
  else
    echo "🔹 启动：$name"
    open -a "$name" 2>/dev/null || echo "⚠️ 未找到或无法启动：$name"
    sleep 0.8
    # 激活一次，确保菜单栏 / 辅助功能类 App 初始化成功
    osascript -e 'try
      tell application "'"$name"'" to activate
    end try' >/dev/null 2>&1
    # 如果终端有辅助功能权限则隐藏窗口
    osascript -e 'tell application "System Events"
      if (name of processes) contains "'"$name"'" then
        try
          set visible of process "'"$name"'" to false
        end try
      end if
    end tell' >/dev/null 2>&1
    echo "✅ 已启动：$name"
  fi
done
echo "🎉 所有未启动的应用已成功开启！"
'''


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
