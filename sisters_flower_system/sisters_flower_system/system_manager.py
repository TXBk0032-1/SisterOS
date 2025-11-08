#!/usr/bin/env python3
"""
姐妹花销售系统 - 统一管理工具
Sisters Flower Sales System - Unified Management Tool

功能：
1. 系统安装和配置
2. 服务管理
3. 备份和恢复
4. 系统监控
5. 维护任务
6. 健康检查
7. 用户界面

作者: MiniMax Agent
版本: 1.0
"""

import os
import sys
import json
import time
import argparse
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class SystemManager:
    """系统管理器"""
    
    def __init__(self):
        self.install_dir = current_dir
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        self.backup_dir = self.install_dir / "backup"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 系统信息
        self.system_info = {
            "platform": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "install_dir": str(self.install_dir),
            "version": "4.0"
        }
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        directories = [self.config_dir, self.data_dir, self.logs_dir, self.backup_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """检查系统要求"""
        requirements = {
            "python_version": {"required": "3.8+", "current": f"{sys.version_info.major}.{sys.version_info.minor}", "status": "unknown"},
            "disk_space": {"required": "500MB", "available": 0, "status": "unknown"},
            "memory": {"required": "2GB", "available": 0, "status": "unknown"},
            "dependencies": {"status": "unknown"},
            "overall": "unknown"
        }
        
        # 检查Python版本
        if sys.version_info >= (3, 8):
            requirements["python_version"]["status"] = "ok"
        else:
            requirements["python_version"]["status"] = "fail"
        
        # 检查磁盘空间
        try:
            import shutil
            free_space = shutil.disk_usage(self.install_dir).free
            requirements["disk_space"]["available"] = f"{free_space / 1024 / 1024 / 1024:.1f}GB"
            if free_space > 500 * 1024 * 1024:  # 500MB
                requirements["disk_space"]["status"] = "ok"
            else:
                requirements["disk_space"]["status"] = "fail"
        except:
            pass
        
        # 检查内存
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / 1024 / 1024 / 1024
            requirements["memory"]["available"] = f"{available_gb:.1f}GB"
            if available_gb >= 2:
                requirements["memory"]["status"] = "ok"
            else:
                requirements["memory"]["status"] = "fail"
        except:
            pass
        
        # 检查依赖
        required_modules = ['tkinter', 'sqlite3', 'json', 'threading', 'pathlib']
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if not missing_modules:
            requirements["dependencies"]["status"] = "ok"
        else:
            requirements["dependencies"]["status"] = f"missing: {', '.join(missing_modules)}"
        
        # 总体状态
        all_ok = all(
            req["status"] in ["ok"] 
            for key, req in requirements.items() 
            if key not in ["overall"]
        )
        requirements["overall"] = "ok" if all_ok else "fail"
        
        return requirements
    
    def install_system(self) -> bool:
        """安装系统"""
        print("🌸 姐妹花销售系统 - 自动安装")
        print("=" * 50)
        
        try:
            # 1. 检查系统要求
            requirements = self.check_system_requirements()
            print("检查系统要求...")
            if requirements["overall"] != "ok":
                print("❌ 系统要求检查失败:")
                for key, req in requirements.items():
                    if key != "overall" and req["status"] not in ["ok"]:
                        print(f"  ❌ {key}: {req['status']}")
                return False
            print("✅ 系统要求检查通过")
            
            # 2. 运行自动安装脚本
            print("\n运行自动安装...")
            install_script = self.install_dir / "install.py"
            if install_script.exists():
                result = subprocess.run([sys.executable, str(install_script)], 
                                      cwd=str(self.install_dir))
                if result.returncode != 0:
                    print("❌ 自动安装失败")
                    return False
                print("✅ 自动安装完成")
            else:
                print("⚠️ 安装脚本不存在，跳过自动安装")
            
            # 3. 初始化数据库
            print("\n初始化数据库...")
            db_init_script = self.install_dir / "db_config_init.py"
            if db_init_script.exists():
                cmd = [
                    sys.executable, str(db_init_script), 
                    "init-db", 
                    "--db-path", str(self.data_dir / "sisters_flowers_system.db"),
                    "--config-dir", str(self.config_dir)
                ]
                result = subprocess.run(cmd, cwd=str(self.install_dir))
                if result.returncode != 0:
                    print("⚠️ 数据库初始化失败，但继续安装")
                else:
                    print("✅ 数据库初始化完成")
            
            # 4. 创建系统配置
            print("\n创建系统配置...")
            self._create_system_config()
            print("✅ 系统配置创建完成")
            
            # 5. 验证安装
            print("\n验证安装...")
            if self._verify_installation():
                print("✅ 安装验证通过")
            else:
                print("⚠️ 安装验证失败")
            
            print("\n🎉 系统安装完成!")
            return True
            
        except Exception as e:
            print(f"❌ 安装过程出错: {e}")
            return False
    
    def _create_system_config(self):
        """创建系统配置"""
        config = {
            "system": {
                "name": "姐妹花销售系统",
                "version": "4.0",
                "install_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "install_dir": str(self.install_dir)
            },
            "paths": {
                "config_dir": str(self.config_dir),
                "data_dir": str(self.data_dir),
                "logs_dir": str(self.logs_dir),
                "backup_dir": str(self.backup_dir)
            },
            "features": {
                "auto_backup": True,
                "system_monitor": True,
                "service_management": True,
                "user_interface": True
            }
        }
        
        config_file = self.config_dir / "system.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _verify_installation(self) -> bool:
        """验证安装"""
        try:
            # 检查关键文件
            required_files = [
                "enhanced_sales_system.py",
                "requirements.txt",
                "install.py"
            ]
            
            for file_name in required_files:
                file_path = self.install_dir / file_name
                if not file_path.exists():
                    print(f"  ❌ 缺少文件: {file_name}")
                    return False
            
            # 检查数据库
            db_file = self.data_dir / "sisters_flowers_system.db"
            if db_file.exists():
                print("  ✅ 数据库文件存在")
            else:
                print("  ⚠️ 数据库文件不存在")
            
            # 检查配置
            if (self.config_dir / "system.json").exists():
                print("  ✅ 配置文件存在")
            else:
                print("  ⚠️ 配置文件不存在")
            
            return True
            
        except Exception as e:
            print(f"验证安装时出错: {e}")
            return False
    
    def start_application(self) -> bool:
        """启动应用程序"""
        try:
            app_script = self.install_dir / "enhanced_sales_system.py"
            if not app_script.exists():
                print("❌ 应用程序文件不存在")
                return False
            
            print("🚀 启动应用程序...")
            subprocess.Popen([sys.executable, str(app_script)], 
                           cwd=str(self.install_dir))
            print("✅ 应用程序已启动")
            return True
            
        except Exception as e:
            print(f"❌ 启动应用程序失败: {e}")
            return False
    
    def show_status(self) -> Dict[str, Any]:
        """显示系统状态"""
        status = {
            "system": self.system_info,
            "installation": {},
            "services": {},
            "resources": {}
        }
        
        # 安装状态
        status["installation"] = {
            "installed": (self.config_dir / "system.json").exists(),
            "config_exists": (self.config_dir / "app_config.json").exists(),
            "database_exists": (self.data_dir / "sisters_flowers_system.db").exists()
        }
        
        # 资源使用情况
        try:
            import psutil
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.install_dir))
            
            status["resources"] = {
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
                "cpu_count": psutil.cpu_count()
            }
        except:
            pass
        
        return status
    
    def run_maintenance(self) -> bool:
        """运行维护任务"""
        try:
            print("🔧 运行系统维护...")
            
            # 1. 运行监控器的维护功能
            monitor_script = self.install_dir / "system_monitor.py"
            if monitor_script.exists():
                cmd = [sys.executable, str(monitor_script), "maintenance", "--cleanup", "--vacuum"]
                result = subprocess.run(cmd, cwd=str(self.install_dir))
                if result.returncode == 0:
                    print("  ✅ 系统清理完成")
                else:
                    print("  ⚠️ 系统清理部分完成")
            
            # 2. 运行备份清理
            backup_script = self.install_dir / "backup_recovery.py"
            if backup_script.exists():
                cmd = [sys.executable, str(backup_script), "cleanup"]
                result = subprocess.run(cmd, cwd=str(self.install_dir))
                if result.returncode == 0:
                    print("  ✅ 备份清理完成")
            
            print("✅ 维护任务完成")
            return True
            
        except Exception as e:
            print(f"❌ 维护任务失败: {e}")
            return False

class ManagementGUI:
    """管理工具GUI界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.manager = SystemManager()
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        self.root.title("姐妹花销售系统 - 管理工具")
        self.root.geometry("800x600")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="姐妹花销售系统 - 管理中心", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 系统状态卡片
        self.create_status_card(main_frame)
        
        # 操作按钮
        self.create_action_buttons(main_frame)
        
        # 日志显示区域
        self.create_log_area(main_frame)
        
        # 状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def create_status_card(self, parent):
        """创建状态卡片"""
        status_frame = ttk.LabelFrame(parent, text="系统状态", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 获取系统状态
        status = self.manager.show_status()
        
        # 显示状态信息
        ttk.Label(status_frame, text=f"系统版本: {status['system']['version']}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(status_frame, text=f"Python版本: {status['system']['python_version']}").grid(row=0, column=1, sticky=tk.W)
        ttk.Label(status_frame, text=f"安装路径: {status['system']['install_dir']}").grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        # 安装状态
        install_status = "✅ 已安装" if status['installation']['installed'] else "❌ 未安装"
        ttk.Label(status_frame, text=f"安装状态: {install_status}").grid(row=2, column=0, sticky=tk.W)
        
        # 资源使用情况
        if 'resources' in status and status['resources']:
            res = status['resources']
            ttk.Label(status_frame, text=f"内存使用: {res.get('memory_percent', 0):.1f}%").grid(row=3, column=0, sticky=tk.W)
            ttk.Label(status_frame, text=f"磁盘使用: {res.get('disk_percent', 0):.1f}%").grid(row=3, column=1, sticky=tk.W)
    
    def create_action_buttons(self, parent):
        """创建操作按钮"""
        button_frame = ttk.LabelFrame(parent, text="系统操作", padding="10")
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 第一行按钮
        row1 = ttk.Frame(button_frame)
        row1.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(row1, text="系统安装", command=self.install_system).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="启动应用", command=self.start_application).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="系统维护", command=self.run_maintenance).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="系统检查", command=self.system_check).pack(side=tk.LEFT, padx=(0, 5))
        
        # 第二行按钮
        row2 = ttk.Frame(button_frame)
        row2.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        ttk.Button(row2, text="备份管理", command=self.backup_management).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2, text="监控面板", command=self.open_monitor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2, text="服务管理", command=self.service_management).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row2, text="帮助文档", command=self.show_help).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_log_area(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def log_message(self, message: str, level: str = "INFO"):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # 更新状态栏
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def install_system(self):
        """系统安装"""
        def run_install():
            self.log_message("开始系统安装...")
            result = self.manager.install_system()
            if result:
                self.log_message("系统安装完成", "SUCCESS")
                messagebox.showinfo("安装完成", "系统安装成功完成！")
            else:
                self.log_message("系统安装失败", "ERROR")
                messagebox.showerror("安装失败", "系统安装过程中出现错误")
        
        threading.Thread(target=run_install, daemon=True).start()
    
    def start_application(self):
        """启动应用程序"""
        self.log_message("启动应用程序...")
        result = self.manager.start_application()
        if result:
            self.log_message("应用程序已启动", "SUCCESS")
        else:
            self.log_message("应用程序启动失败", "ERROR")
    
    def run_maintenance(self):
        """运行维护"""
        def run_maint():
            self.log_message("开始系统维护...")
            result = self.manager.run_maintenance()
            if result:
                self.log_message("系统维护完成", "SUCCESS")
                messagebox.showinfo("维护完成", "系统维护任务完成！")
            else:
                self.log_message("系统维护失败", "ERROR")
                messagebox.showerror("维护失败", "系统维护过程中出现错误")
        
        threading.Thread(target=run_maint, daemon=True).start()
    
    def system_check(self):
        """系统检查"""
        def run_check():
            self.log_message("开始系统检查...")
            
            # 检查系统要求
            requirements = self.manager.check_system_requirements()
            
            if requirements["overall"] == "ok":
                self.log_message("系统检查通过", "SUCCESS")
                messagebox.showinfo("检查完成", "系统要求检查通过！")
            else:
                self.log_message("系统检查失败", "ERROR")
                error_msg = "系统要求检查失败：\n"
                for key, req in requirements.items():
                    if key != "overall" and req["status"] not in ["ok"]:
                        error_msg += f"• {key}: {req['status']}\n"
                messagebox.showerror("检查失败", error_msg)
        
        threading.Thread(target=run_check, daemon=True).start()
    
    def backup_management(self):
        """备份管理"""
        self.log_message("打开备份管理...")
        # 这里可以打开备份管理界面
        messagebox.showinfo("备份管理", "备份管理功能即将推出...")
    
    def open_monitor(self):
        """打开监控面板"""
        self.log_message("打开监控面板...")
        monitor_script = self.manager.install_dir / "system_monitor.py"
        if monitor_script.exists():
            subprocess.Popen([sys.executable, str(monitor_script), "check"], 
                           cwd=str(self.manager.install_dir))
        else:
            messagebox.showerror("错误", "监控工具不存在")
    
    def service_management(self):
        """服务管理"""
        self.log_message("打开服务管理...")
        service_script = self.manager.install_dir / "service_manager.py"
        if service_script.exists():
            subprocess.Popen([sys.executable, str(service_script), "status"], 
                           cwd=str(self.manager.install_dir))
        else:
            messagebox.showerror("错误", "服务管理工具不存在")
    
    def show_help(self):
        """显示帮助"""
        help_text = """
姐妹花销售系统 - 管理工具帮助

系统操作：
• 系统安装：安装系统所需的组件和依赖
• 启动应用：启动主应用程序
• 系统维护：清理系统垃圾，优化性能
• 系统检查：检查系统环境和依赖

备份管理：
• 自动备份：按计划自动备份数据
• 手动备份：立即创建备份
• 备份恢复：从备份恢复数据

监控面板：
• 实时监控：监控系统性能和状态
• 健康检查：检查系统健康状况
• 错误分析：分析系统错误日志

服务管理：
• 服务安装：将系统注册为系统服务
• 服务控制：启动/停止/重启系统服务
• 状态监控：监控服务运行状态

更多信息请查看用户手册。
        """
        
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助文档")
        help_window.geometry("600x400")
        
        help_text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def run(self):
        """运行GUI"""
        self.log_message("管理工具已启动")
        self.root.mainloop()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="姐妹花销售系统 - 统一管理工具")
    parser.add_argument("--gui", action="store_true", help="启动图形界面")
    parser.add_argument("--install", action="store_true", help="执行系统安装")
    parser.add_argument("--start", action="store_true", help="启动应用程序")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--maintenance", action="store_true", help="运行系统维护")
    parser.add_argument("--check", action="store_true", help="系统检查")
    
    args = parser.parse_args()
    
    manager = SystemManager()
    
    # 如果没有参数，启动GUI
    if not any(vars(args).values()):
        gui = ManagementGUI()
        gui.run()
        return
    
    try:
        if args.install:
            manager.install_system()
        elif args.start:
            manager.start_application()
        elif args.status:
            status = manager.show_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        elif args.maintenance:
            manager.run_maintenance()
        elif args.check:
            requirements = manager.check_system_requirements()
            print(json.dumps(requirements, ensure_ascii=False, indent=2))
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()