#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开机启动管理器 - 可视化配置工具
Boot Startup Manager - Visual Configuration Tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import subprocess
import platform
from pathlib import Path
from typing import List, Dict

class StartupManager:
    def __init__(self, root):
        self.root = root
        self.root.title("开机启动管理器 - Boot Startup Manager")
        self.root.geometry("900x700")

        # 配置文件路径
        self.config_file = Path.home() / ".startup_manager_config.json"
        self.script_file = Path.home() / "startup_apps.sh"

        # 默认应用列表（从完美版本脚本读取）
        self.default_apps = [
            "Antinote", "BetterTouchTool", "Bob", "CleanShot X", "Clicknow",
            "Dropover", "Hookmark", "Magnet", "Mouseless", "One Switch",
            "PixelSnap", "PopClip", "Raycast", "Screen Studio", "Shottr",
            "Snipaste", "superwhisper", "Surge", "Swish", "Voicenotes"
        ]

        # 当前应用列表
        self.current_apps = []

        # 已安装应用缓存
        self.installed_apps = []

        # 创建UI
        self.create_ui()

        # 加载配置
        self.load_config()

        # 扫描已安装应用
        self.scan_installed_apps()

    def create_ui(self):
        """创建用户界面"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="🚀 开机启动管理器",
            font=("Arial", 18, "bold"),
            pady=10
        )
        title_label.pack()

        # 主容器
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左侧 - 当前启动项列表
        left_frame = tk.LabelFrame(main_frame, text="当前启动项", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 列表框架
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 启动项列表
        self.app_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            selectmode=tk.SINGLE
        )
        self.app_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.app_listbox.yview)

        # 左侧按钮
        left_btn_frame = tk.Frame(left_frame)
        left_btn_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            left_btn_frame,
            text="↑ 上移",
            command=self.move_up,
            width=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            left_btn_frame,
            text="↓ 下移",
            command=self.move_down,
            width=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            left_btn_frame,
            text="🗑️ 删除",
            command=self.remove_app,
            width=10,
            fg="red"
        ).pack(side=tk.LEFT, padx=2)

        # 右侧 - 添加应用
        right_frame = tk.LabelFrame(main_frame, text="添加应用", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 搜索框
        search_frame = tk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="🔍 搜索：").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_apps())

        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Button(
            search_frame,
            text="🔄 刷新",
            command=self.scan_installed_apps,
            width=8
        ).pack(side=tk.RIGHT)

        # 已安装应用列表
        installed_list_frame = tk.Frame(right_frame)
        installed_list_frame.pack(fill=tk.BOTH, expand=True)

        installed_scrollbar = tk.Scrollbar(installed_list_frame)
        installed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.installed_listbox = tk.Listbox(
            installed_list_frame,
            yscrollcommand=installed_scrollbar.set,
            font=("Arial", 11),
            selectmode=tk.SINGLE
        )
        self.installed_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        installed_scrollbar.config(command=self.installed_listbox.yview)

        # 右侧按钮
        right_btn_frame = tk.Frame(right_frame)
        right_btn_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            right_btn_frame,
            text="➕ 添加选中",
            command=self.add_selected_app,
            width=15,
            fg="green"
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            right_btn_frame,
            text="📝 手动输入",
            command=self.add_manual_app,
            width=15
        ).pack(side=tk.LEFT, padx=2)

        # 底部操作按钮
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(
            bottom_frame,
            text="💾 保存配置",
            command=self.save_config,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="📜 生成启动脚本",
            command=self.generate_script,
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="🚀 立即启动应用",
            command=self.run_startup,
            font=("Arial", 11, "bold"),
            bg="#FF9800",
            fg="white",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="🔄 恢复默认",
            command=self.restore_defaults,
            font=("Arial", 11),
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=5)

    def scan_installed_apps(self):
        """扫描已安装的应用程序"""
        self.installed_apps = []

        if platform.system() == "Darwin":  # macOS
            app_dirs = ["/Applications", str(Path.home() / "Applications")]
        elif platform.system() == "Windows":
            # Windows应用路径
            app_dirs = [
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                str(Path.home() / "AppData" / "Local" / "Programs")
            ]
        else:  # Linux
            app_dirs = [
                "/usr/share/applications",
                str(Path.home() / ".local" / "share" / "applications")
            ]

        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                try:
                    if platform.system() == "Darwin":
                        # macOS: 查找.app文件
                        for item in os.listdir(app_dir):
                            if item.endswith('.app'):
                                app_name = item.replace('.app', '')
                                if app_name not in self.installed_apps:
                                    self.installed_apps.append(app_name)
                    elif platform.system() == "Windows":
                        # Windows: 查找.exe文件
                        for root, dirs, files in os.walk(app_dir):
                            for file in files:
                                if file.endswith('.exe'):
                                    app_name = file.replace('.exe', '')
                                    if app_name not in self.installed_apps:
                                        self.installed_apps.append(app_name)
                            # 只扫描一层目录，避免太慢
                            break
                    else:
                        # Linux: 查找.desktop文件
                        for item in os.listdir(app_dir):
                            if item.endswith('.desktop'):
                                app_name = item.replace('.desktop', '')
                                if app_name not in self.installed_apps:
                                    self.installed_apps.append(app_name)
                except PermissionError:
                    continue

        # 排序
        self.installed_apps.sort()

        # 更新显示
        self.filter_apps()

    def filter_apps(self):
        """根据搜索词过滤应用"""
        search_term = self.search_var.get().lower()

        self.installed_listbox.delete(0, tk.END)

        for app in self.installed_apps:
            if search_term in app.lower():
                self.installed_listbox.insert(tk.END, app)

    def add_selected_app(self):
        """添加选中的应用"""
        selection = self.installed_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个应用")
            return

        app_name = self.installed_listbox.get(selection[0])

        if app_name in self.current_apps:
            messagebox.showinfo("提示", f"'{app_name}' 已在启动列表中")
            return

        self.current_apps.append(app_name)
        self.update_app_listbox()
        messagebox.showinfo("成功", f"已添加 '{app_name}'")

    def add_manual_app(self):
        """手动输入应用名称"""
        dialog = tk.Toplevel(self.root)
        dialog.title("手动添加应用")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="请输入应用名称：", font=("Arial", 11)).pack(pady=10)

        app_entry = tk.Entry(dialog, font=("Arial", 11), width=30)
        app_entry.pack(pady=5)
        app_entry.focus()

        def add():
            app_name = app_entry.get().strip()
            if not app_name:
                messagebox.showwarning("警告", "应用名称不能为空", parent=dialog)
                return

            if app_name in self.current_apps:
                messagebox.showinfo("提示", f"'{app_name}' 已在启动列表中", parent=dialog)
                return

            self.current_apps.append(app_name)
            self.update_app_listbox()
            dialog.destroy()
            messagebox.showinfo("成功", f"已添加 '{app_name}'")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="添加", command=add, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)

        app_entry.bind('<Return>', lambda e: add())

    def remove_app(self):
        """删除选中的应用"""
        selection = self.app_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的应用")
            return

        index = selection[0]
        app_name = self.current_apps[index]

        if messagebox.askyesno("确认", f"确定要删除 '{app_name}' 吗？"):
            self.current_apps.pop(index)
            self.update_app_listbox()

    def move_up(self):
        """上移选中项"""
        selection = self.app_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index > 0:
            self.current_apps[index], self.current_apps[index-1] = \
                self.current_apps[index-1], self.current_apps[index]
            self.update_app_listbox()
            self.app_listbox.selection_set(index-1)

    def move_down(self):
        """下移选中项"""
        selection = self.app_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index < len(self.current_apps) - 1:
            self.current_apps[index], self.current_apps[index+1] = \
                self.current_apps[index+1], self.current_apps[index]
            self.update_app_listbox()
            self.app_listbox.selection_set(index+1)

    def update_app_listbox(self):
        """更新启动项列表显示"""
        self.app_listbox.delete(0, tk.END)
        for i, app in enumerate(self.current_apps, 1):
            self.app_listbox.insert(tk.END, f"{i}. {app}")

    def save_config(self):
        """保存配置到文件"""
        config = {
            "apps": self.current_apps
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"配置已保存到：\n{self.config_file}")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")

    def load_config(self):
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.current_apps = config.get("apps", [])
            except Exception as e:
                print(f"加载配置失败：{str(e)}")
                self.current_apps = self.default_apps.copy()
        else:
            self.current_apps = self.default_apps.copy()

        self.update_app_listbox()

    def restore_defaults(self):
        """恢复默认配置"""
        if messagebox.askyesno("确认", "确定要恢复到默认配置吗？\n当前配置将被覆盖。"):
            self.current_apps = self.default_apps.copy()
            self.update_app_listbox()
            messagebox.showinfo("成功", "已恢复默认配置")

    def generate_script(self):
        """生成启动脚本"""
        if not self.current_apps:
            messagebox.showwarning("警告", "启动列表为空，请先添加应用")
            return

        script_content = self._get_script_content()

        try:
            with open(self.script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # 设置可执行权限
            if platform.system() != "Windows":
                os.chmod(self.script_file, 0o755)

            messagebox.showinfo(
                "成功",
                f"启动脚本已生成：\n{self.script_file}\n\n"
                f"包含 {len(self.current_apps)} 个应用"
            )
        except Exception as e:
            messagebox.showerror("错误", f"生成脚本失败：{str(e)}")

    def _get_script_content(self) -> str:
        """获取脚本内容"""
        apps_array = '\n'.join([f'"{app}"' for app in self.current_apps])

        if platform.system() == "Darwin":  # macOS
            return f'''#!/bin/bash
# 开机启动脚本 - 自动生成
# Boot Startup Script - Auto Generated

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
        elif platform.system() == "Windows":  # Windows
            apps_list = '\n'.join([f'    "{app}",' for app in self.current_apps])
            return f'''@echo off
REM 开机启动脚本 - 自动生成
REM Boot Startup Script - Auto Generated
chcp 65001 >nul

echo 🚀 启动应用程序...

{chr(10).join([f'start "" "{app}"' for app in self.current_apps])}

echo 🎉 所有应用已启动！
pause
'''
        else:  # Linux
            return f'''#!/bin/bash
# 开机启动脚本 - 自动生成
# Boot Startup Script - Auto Generated

apps=(
{apps_array}
)

echo "🚀 启动应用程序..."
for app in "${{apps[@]}}"; do
  if command -v "$app" &> /dev/null; then
    echo "🔹 启动：$app"
    "$app" &
  else
    echo "⚠️ 未找到：$app"
  fi
done
echo "🎉 所有应用已启动！"
'''

    def run_startup(self):
        """立即运行启动脚本"""
        if not self.current_apps:
            messagebox.showwarning("警告", "启动列表为空，请先添加应用")
            return

        # 先生成脚本
        self.generate_script()

        # 创建输出窗口
        output_window = tk.Toplevel(self.root)
        output_window.title("启动日志")
        output_window.geometry("600x400")

        output_text = scrolledtext.ScrolledText(
            output_window,
            font=("Courier", 10),
            wrap=tk.WORD
        )
        output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    [str(self.script_file)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    shell=True
                )
            else:
                process = subprocess.Popen(
                    ['/bin/bash', str(self.script_file)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

            # 实时显示输出
            for line in process.stdout:
                output_text.insert(tk.END, line)
                output_text.see(tk.END)
                output_window.update()

            process.wait()

            if process.returncode == 0:
                output_text.insert(tk.END, "\n✅ 执行完成！\n")
            else:
                output_text.insert(tk.END, f"\n⚠️ 执行完成，返回码：{process.returncode}\n")

        except Exception as e:
            output_text.insert(tk.END, f"\n❌ 错误：{str(e)}\n")

def main():
    root = tk.Tk()
    app = StartupManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
