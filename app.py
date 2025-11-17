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


@app.route('/api/configs', methods=['GET'])
def get_all_configs():
    """获取所有配置方案"""
    full_config = load_full_config()
    current = full_config.get('current', 'default')
    configs = full_config.get('configs', {})

    # 转换为前端需要的格式
    config_list = []
    for config_id, config_data in configs.items():
        config_list.append({
            "id": config_id,
            "name": config_data.get('name', config_id),
            "apps": config_data.get('apps', []),
            "isCurrent": config_id == current
        })

    return jsonify({
        "success": True,
        "current": current,
        "configs": config_list
    })


@app.route('/api/configs/switch', methods=['POST'])
def switch_config():
    """切换到指定配置"""
    data = request.get_json()
    config_id = data.get('id', '')

    if not config_id:
        return jsonify({"success": False, "message": "配置ID不能为空"}), 400

    full_config = load_full_config()

    if config_id not in full_config['configs']:
        return jsonify({"success": False, "message": "配置不存在"}), 404

    # 切换当前配置
    full_config['current'] = config_id

    if save_full_config(full_config):
        apps = full_config['configs'][config_id].get('apps', [])
        return jsonify({
            "success": True,
            "message": f"已切换到：{full_config['configs'][config_id]['name']}",
            "apps": apps
        })
    else:
        return jsonify({"success": False, "message": "切换失败"}), 500


@app.route('/api/configs/save', methods=['POST'])
def save_new_config():
    """另存为新配置"""
    data = request.get_json()
    config_name = data.get('name', '').strip()
    apps = data.get('apps', [])

    if not config_name:
        return jsonify({"success": False, "message": "配置名称不能为空"}), 400

    full_config = load_full_config()

    # 生成唯一ID（使用时间戳）
    import time
    config_id = f"config_{int(time.time())}"

    # 检查名称是否重复
    for existing_config in full_config['configs'].values():
        if existing_config['name'] == config_name:
            return jsonify({"success": False, "message": "配置名称已存在"}), 400

    # 添加新配置
    full_config['configs'][config_id] = {
        "name": config_name,
        "apps": apps
    }

    if save_full_config(full_config):
        return jsonify({
            "success": True,
            "message": f"配置'{config_name}'已保存",
            "id": config_id
        })
    else:
        return jsonify({"success": False, "message": "保存失败"}), 500


@app.route('/api/configs/rename', methods=['POST'])
def rename_config():
    """重命名配置"""
    data = request.get_json()
    config_id = data.get('id', '')
    new_name = data.get('name', '').strip()

    if not config_id or not new_name:
        return jsonify({"success": False, "message": "参数不能为空"}), 400

    # 不允许重命名默认配置
    if config_id == 'default':
        return jsonify({"success": False, "message": "默认配置不能重命名"}), 400

    full_config = load_full_config()

    if config_id not in full_config['configs']:
        return jsonify({"success": False, "message": "配置不存在"}), 404

    # 检查新名称是否重复
    for cid, existing_config in full_config['configs'].items():
        if cid != config_id and existing_config['name'] == new_name:
            return jsonify({"success": False, "message": "配置名称已存在"}), 400

    # 重命名
    full_config['configs'][config_id]['name'] = new_name

    if save_full_config(full_config):
        return jsonify({
            "success": True,
            "message": f"已重命名为'{new_name}'"
        })
    else:
        return jsonify({"success": False, "message": "重命名失败"}), 500


@app.route('/api/configs/delete', methods=['POST'])
def delete_config():
    """删除配置"""
    data = request.get_json()
    config_id = data.get('id', '')

    if not config_id:
        return jsonify({"success": False, "message": "配置ID不能为空"}), 400

    # 不允许删除默认配置
    if config_id == 'default':
        return jsonify({"success": False, "message": "默认配置不能删除"}), 400

    full_config = load_full_config()

    if config_id not in full_config['configs']:
        return jsonify({"success": False, "message": "配置不存在"}), 404

    config_name = full_config['configs'][config_id]['name']

    # 如果删除的是当前配置，切换到默认配置
    if full_config['current'] == config_id:
        full_config['current'] = 'default'

    # 删除配置
    del full_config['configs'][config_id]

    if save_full_config(full_config):
        # 如果删除的是当前配置，返回默认配置的apps
        apps = full_config['configs']['default'].get('apps', [])
        return jsonify({
            "success": True,
            "message": f"已删除配置'{config_name}'",
            "apps": apps if full_config['current'] == 'default' else None
        })
    else:
        return jsonify({"success": False, "message": "删除失败"}), 500


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

                # 兼容旧格式（直接是apps数组）
                if isinstance(config, dict) and 'apps' in config and 'configs' not in config:
                    # 旧格式，转换为新格式
                    old_apps = config.get('apps', [])
                    config = {
                        "current": "default",
                        "configs": {
                            "default": {
                                "name": "默认配置",
                                "apps": old_apps if old_apps else DEFAULT_APPS.copy()
                            }
                        }
                    }
                    save_full_config(config)

                # 新格式
                if 'configs' in config:
                    current = config.get('current', 'default')
                    if current in config['configs']:
                        return config['configs'][current].get('apps', DEFAULT_APPS.copy())

                return DEFAULT_APPS.copy()
        except Exception as e:
            print(f"加载配置失败：{e}")
            return DEFAULT_APPS.copy()
    else:
        # 首次使用，创建默认配置
        default_config = {
            "current": "default",
            "configs": {
                "default": {
                    "name": "默认配置",
                    "apps": DEFAULT_APPS.copy()
                }
            }
        }
        save_full_config(default_config)
        return DEFAULT_APPS.copy()


def save_config(apps):
    """保存当前配置的apps"""
    try:
        # 读取完整配置
        full_config = load_full_config()
        current = full_config.get('current', 'default')

        # 更新当前配置的apps
        if current in full_config['configs']:
            full_config['configs'][current]['apps'] = apps

        save_full_config(full_config)
        return True
    except Exception as e:
        print(f"保存配置失败：{e}")
        return False


def load_full_config():
    """加载完整配置（包括所有配置方案）"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)

                # 兼容旧格式
                if isinstance(config, dict) and 'apps' in config and 'configs' not in config:
                    old_apps = config.get('apps', [])
                    config = {
                        "current": "default",
                        "configs": {
                            "default": {
                                "name": "默认配置",
                                "apps": old_apps if old_apps else DEFAULT_APPS.copy()
                            }
                        }
                    }

                return config
        except Exception as e:
            print(f"加载完整配置失败：{e}")

    # 返回默认配置
    return {
        "current": "default",
        "configs": {
            "default": {
                "name": "默认配置",
                "apps": DEFAULT_APPS.copy()
            }
        }
    }


def save_full_config(config):
    """保存完整配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存完整配置失败：{e}")
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
