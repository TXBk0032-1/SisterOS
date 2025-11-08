#!/usr/bin/env python3
"""
姐妹花销售系统 - 快速启动和系统检查工具
Sisters Flower Sales System - Quick Start and System Check Tool

功能：
1. 快速启动系统
2. 系统环境检查
3. 依赖检查
4. 故障诊断
5. 快速修复

作者: MiniMax Agent
版本: 1.0
"""

import argparse
import importlib
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any


class QuickStarter:
    """快速启动器"""
    
    def __init__(self):
        self.install_dir = Path(__file__).parent
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        
        # 检查文件路径
        self.app_script = self.install_dir / "enhanced_sales_system.py"
        self.install_script = self.install_dir / "install.py"
        self.config_file = self.config_dir / "app_config.json"
        self.db_file = self.data_dir / "sisters_flowers_system.db"
        
        # 系统信息
        self.system_info = {
            "platform": platform.system(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "install_dir": str(self.install_dir)
        }
    
    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                🌸 姐妹花销售系统 v4.0 🌸                     ║
║             Sisters Flower Sales System                     ║
║                                                              ║
║  🎯 现代化销售管理系统                                        ║
║  🔧 自动安装和配置                                          ║
║  📊 完整的数据分析功能                                       ║
║  🛡️ 安全的用户管理                                          ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_installation(self) -> Dict[str, Any]:
        """检查安装状态"""
        status = {
            "installed": False,
            "config_exists": False,
            "database_exists": False,
            "dependencies_ok": False,
            "ready_to_start": False,
            "issues": []
        }
        
        # 检查配置文件
        if self.config_file.exists():
            status["config_exists"] = True
        else:
            status["issues"].append("配置文件不存在")
        
        # 检查数据库
        if self.db_file.exists():
            status["database_exists"] = True
        else:
            status["issues"].append("数据库文件不存在")
        
        # 检查依赖
        missing_deps = self._check_dependencies()
        if not missing_deps:
            status["dependencies_ok"] = True
        else:
            status["issues"].append(f"缺少依赖: {', '.join(missing_deps)}")
        
        # 检查主程序
        if not self.app_script.exists():
            status["issues"].append("主程序文件不存在")
        
        # 总体安装状态
        status["installed"] = (
            status["config_exists"] and 
            status["database_exists"] and 
            status["dependencies_ok"] and 
            self.app_script.exists()
        )
        
        # 是否可以启动
        status["ready_to_start"] = status["installed"] and self.app_script.exists()
        
        return status
    
    def _check_dependencies(self) -> List[str]:
        """检查依赖包"""
        required_modules = {
            'tkinter': 'Python GUI库',
            'sqlite3': 'SQLite数据库',
            'json': 'JSON处理',
            'threading': '多线程支持',
            'pathlib': '路径处理',
            'datetime': '日期时间处理'
        }
        
        # 可选模块
        optional_modules = {
            'ttkbootstrap': '现代化UI主题',
            'pywinstyles': 'Windows样式',
            'win32mica': 'Windows 11特效',
            'psutil': '系统监控',
            'pillow': '图像处理',
            'matplotlib': '图表绘制',
            'pandas': '数据分析'
        }
        
        missing_required = []
        missing_optional = []
        
        # 检查必需模块
        for module, description in required_modules.items():
            try:
                importlib.import_module(module)
            except ImportError:
                missing_required.append(f"{module} ({description})")
        
        # 检查可选模块
        for module, description in optional_modules.items():
            try:
                importlib.import_module(module)
            except ImportError:
                missing_optional.append(f"{module} ({description})")
        
        return missing_required + missing_optional
    
    def auto_install_if_needed(self) -> bool:
        """必要时自动安装"""
        status = self.check_installation()
        
        if status["ready_to_start"]:
            return True
        
        print("🔧 检测到系统未完全安装，正在尝试自动修复...")
        
        # 如果安装脚本存在，尝试运行
        if self.install_script.exists():
            print("运行自动安装程序...")
            try:
                result = subprocess.run([
                    sys.executable, str(self.install_script)
                ], cwd=str(self.install_dir), timeout=300)
                
                if result.returncode == 0:
                    print("✅ 自动安装成功")
                    return True
                else:
                    print("❌ 自动安装失败")
                    return False
            except subprocess.TimeoutExpired:
                print("❌ 安装超时")
                return False
            except Exception as e:
                print(f"❌ 安装出错: {e}")
                return False
        else:
            print("❌ 安装脚本不存在")
            return False
    
    def start_application(self) -> bool:
        """启动应用程序"""
        try:
            if not self.app_script.exists():
                print("❌ 主程序文件不存在")
                return False
            
            print("🚀 启动姐妹花销售系统...")
            print("📍 程序路径:", self.app_script)
            print("💡 如遇问题，请查看日志文件或运行故障诊断")
            
            # 启动程序
            subprocess.Popen([sys.executable, str(self.app_script)], 
                           cwd=str(self.install_dir))
            
            print("✅ 应用程序已启动！")
            return True
            
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def diagnose_issues(self) -> Dict[str, Any]:
        """诊断系统问题"""
        diagnosis = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": self.system_info,
            "installation_status": self.check_installation(),
            "environment_issues": [],
            "suggestions": []
        }
        
        # 检查Python环境
        if sys.version_info < (3, 8):
            diagnosis["environment_issues"].append(
                f"Python版本过低: {sys.version_info.major}.{sys.version_info.minor}, 需要3.8+"
            )
            diagnosis["suggestions"].append("升级Python到3.8或更高版本")
        
        # 检查文件系统权限
        try:
            test_file = self.install_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            diagnosis["environment_issues"].append(f"文件系统权限问题: {e}")
            diagnosis["suggestions"].append("检查安装目录的读写权限")
        
        # 检查端口占用
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('localhost', 8080))
            s.close()
        except OSError:
            diagnosis["environment_issues"].append("端口8080可能被占用")
            diagnosis["suggestions"].append("关闭占用8080端口的程序或修改配置")
        
        # 检查内存和磁盘空间
        try:
            import shutil
            free_space = shutil.disk_usage(self.install_dir).free / 1024 / 1024 / 1024
            if free_space < 1:  # 少于1GB
                diagnosis["environment_issues"].append(f"磁盘空间不足: {free_space:.1f}GB")
                diagnosis["suggestions"].append("清理磁盘空间或更换存储位置")
        except:
            pass
        
        # 检查进程冲突
        try:
            import psutil
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('enhanced_sales_system.py' in str(cmd) for cmd in proc.info['cmdline']):
                        python_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if python_processes:
                diagnosis["environment_issues"].append("检测到已有应用程序实例在运行")
                diagnosis["suggestions"].append("关闭现有实例或重启系统")
        except:
            pass
        
        return diagnosis
    
    def show_system_info(self):
        """显示系统信息"""
        print("📋 系统信息:")
        print(f"  操作系统: {self.system_info['platform']}")
        print(f"  Python版本: {self.system_info['python_version']}")
        print(f"  系统架构: {self.system_info['architecture']}")
        print(f"  安装路径: {self.system_info['install_dir']}")
    
    def run_quick_start(self):
        """运行快速启动"""
        self.print_banner()
        self.show_system_info()
        
        print("\n🔍 检查系统状态...")
        status = self.check_installation()
        
        if status["ready_to_start"]:
            print("✅ 系统已就绪，启动中...")
            self.start_application()
        else:
            print("⚠️ 系统需要配置或修复")
            
            if status["issues"]:
                print("\n发现的问题:")
                for issue in status["issues"]:
                    print(f"  ❌ {issue}")
            
            # 询问是否自动修复
            if self.install_script.exists():
                response = input("\n是否运行自动安装和修复? (Y/n): ").strip().lower()
                if response in ['', 'y', 'yes']:
                    self.auto_install_if_needed()
                    # 重新检查
                    status = self.check_installation()
                    if status["ready_to_start"]:
                        self.start_application()
                    else:
                        print("❌ 自动修复失败，请手动检查系统")
                else:
                    print("请手动运行安装程序: python install.py")
            else:
                print("❌ 未找到安装程序，请手动安装系统")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="姐妹花销售系统 - 快速启动和系统检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python quick_start.py              # 快速启动
  python quick_start.py --check      # 系统检查
  python quick_start.py --diagnose   # 故障诊断
  python quick_start.py --install    # 自动安装
  python quick_start.py --start      # 启动应用
        """
    )
    
    parser.add_argument("--check", action="store_true", help="检查系统状态")
    parser.add_argument("--diagnose", action="store_true", help="运行故障诊断")
    parser.add_argument("--install", action="store_true", help="运行自动安装")
    parser.add_argument("--start", action="store_true", help="启动应用程序")
    parser.add_argument("--info", action="store_true", help="显示系统信息")
    parser.add_argument("--fix", action="store_true", help="尝试自动修复问题")
    
    args = parser.parse_args()
    
    starter = QuickStarter()
    
    try:
        if args.info:
            starter.print_banner()
            starter.show_system_info()
            status = starter.check_installation()
            print(f"\n📊 安装状态:")
            print(f"  已安装: {status['installed']}")
            print(f"  配置文件: {status['config_exists']}")
            print(f"  数据库: {status['database_exists']}")
            print(f"  依赖完整: {status['dependencies_ok']}")
            print(f"  可启动: {status['ready_to_start']}")
        
        elif args.check:
            starter.print_banner()
            status = starter.check_installation()
            print("🔍 系统检查结果:")
            print(f"  ✅ 系统就绪: {status['ready_to_start']}")
            if status["issues"]:
                print("  ❌ 发现问题:")
                for issue in status["issues"]:
                    print(f"    - {issue}")
            else:
                print("  🎉 系统状态良好")
        
        elif args.diagnose:
            starter.print_banner()
            print("🔧 运行系统诊断...")
            diagnosis = starter.diagnose_issues()
            
            print(f"\n📋 诊断结果 ({diagnosis['timestamp']}):")
            
            if diagnosis["environment_issues"]:
                print("  ❌ 发现问题:")
                for issue in diagnosis["environment_issues"]:
                    print(f"    - {issue}")
            else:
                print("  ✅ 未发现环境问题")
            
            if diagnosis["suggestions"]:
                print("\n💡 建议:")
                for suggestion in diagnosis["suggestions"]:
                    print(f"  • {suggestion}")
        
        elif args.install:
            starter.print_banner()
            print("🔧 运行自动安装...")
            success = starter.auto_install_if_needed()
            if success:
                print("✅ 安装完成!")
            else:
                print("❌ 安装失败!")
        
        elif args.start:
            starter.print_banner()
            status = starter.check_installation()
            if status["ready_to_start"]:
                starter.start_application()
            else:
                print("❌ 系统未就绪，无法启动")
                print("请先运行: python quick_start.py --fix")
        
        elif args.fix:
            starter.print_banner()
            print("🔧 尝试自动修复...")
            success = starter.auto_install_if_needed()
            if success:
                print("✅ 修复完成!")
            else:
                print("❌ 修复失败!")
                print("请手动运行: python install.py")
        
        else:
            # 默认运行快速启动
            starter.run_quick_start()
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        print("💡 建议运行故障诊断: python quick_start.py --diagnose")

if __name__ == "__main__":
    main()