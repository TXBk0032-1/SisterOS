#!/usr/bin/env python3
"""
姐妹花销售系统 - 自动安装脚本
Sisters Flower Sales System - Auto Install Script

功能：
1. 检测Python版本
2. 安装依赖包
3. 初始化数据库
4. 创建配置文件
5. 设置系统服务
6. 创建桌面快捷方式

作者: MiniMax Agent
版本: 1.0
"""

import getpass
import json
import os
import platform
import sqlite3
import subprocess
import sys
import time
from pathlib import Path


class AutoInstaller:
    """自动安装器类"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.install_dir = Path(__file__).parent
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        self.backup_dir = self.install_dir / "backup"
        
    def print_banner(self):
        """打印安装横幅"""
        print("=" * 80)
        print("🌸 姐妹花销售系统 - 自动安装器 🌸")
        print("   Sisters Flower Sales System Auto Installer")
        print("=" * 80)
        print(f"检测到系统: {self.system}")
        print(f"Python版本: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"安装目录: {self.install_dir}")
        print("=" * 80)
        
    def check_python_version(self):
        """检查Python版本"""
        print("\n🔍 检查Python版本...")
        if self.python_version.major < 3 or (self.python_version.major == 3 and self.python_version.minor < 8):
            print("❌ 错误: 需要Python 3.8或更高版本")
            print(f"当前版本: {self.python_version.major}.{self.python_version.minor}")
            return False
        print(f"✅ Python版本检查通过: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        return True
        
    def create_directories(self):
        """创建必要的目录"""
        print("\n📁 创建目录结构...")
        directories = [
            self.data_dir,
            self.logs_dir,
            self.backup_dir,
            self.config_dir / "themes",
            self.config_dir / "exports",
            self.config_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ 创建目录: {directory}")
            
    def install_dependencies(self):
        """安装依赖包"""
        print("\n📦 安装依赖包...")
        requirements_file = self.install_dir / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ 错误: requirements.txt文件不存在")
            return False
            
        try:
            # 升级pip
            print("  🔄 升级pip...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # 安装依赖
            print("  📦 安装依赖包...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ 依赖包安装成功")
                return True
            else:
                print(f"  ❌ 依赖包安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ 安装过程中出现错误: {e}")
            return False
            
    def initialize_database(self):
        """初始化数据库"""
        print("\n🗄️ 初始化数据库...")
        db_file = self.data_dir / "sisters_flowers_system.db"
        
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # 创建表结构
            tables = [
                """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )""",
                
                """CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    price REAL NOT NULL,
                    stock INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                
                """CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    customer_name TEXT,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )""",
                
                """CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
                
                """CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
            ]
            
            for table_sql in tables:
                cursor.execute(table_sql)
                print(f"  ✅ 创建表: {table_sql.split('(')[0].split('CREATE TABLE IF NOT EXISTS')[1].strip()}")
            
            # 插入默认设置
            default_settings = [
                ('app_name', '姐妹花销售系统'),
                ('version', '4.0'),
                ('theme', 'light'),
                ('language', 'zh-CN'),
                ('auto_backup', 'true'),
                ('backup_interval', '24'),
            ]
            
            cursor.executemany(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                default_settings
            )
            
            conn.commit()
            conn.close()
            print("  ✅ 数据库初始化完成")
            return True
            
        except Exception as e:
            print(f"  ❌ 数据库初始化失败: {e}")
            return False
            
    def create_config_files(self):
        """创建配置文件"""
        print("\n⚙️ 创建配置文件...")
        
        # 主配置文件
        config = {
            "app": {
                "name": "姐妹花销售系统",
                "version": "4.0",
                "author": "MiniMax Agent",
                "description": "完整的现代化销售管理系统"
            },
            "database": {
                "type": "sqlite",
                "path": str(self.data_dir / "sisters_flowers_system.db"),
                "backup_enabled": True,
                "backup_interval_hours": 24,
                "backup_retention_days": 30
            },
            "ui": {
                "theme": "light",
                "font_family": "Microsoft YaHei UI",
                "font_size": 10,
                "window_size": "1200x800",
                "min_window_size": "800x600"
            },
            "security": {
                "session_timeout_minutes": 60,
                "max_login_attempts": 3,
                "password_min_length": 6,
                "require_strong_password": False
            },
            "backup": {
                "auto_backup": True,
                "backup_interval_hours": 24,
                "backup_retention_days": 30,
                "backup_location": str(self.backup_dir)
            },
            "logging": {
                "level": "INFO",
                "file": str(self.logs_dir / "system.log"),
                "max_file_size_mb": 10,
                "backup_count": 5
            }
        }
        
        config_file = self.config_dir / "app_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 创建配置文件: {config_file}")
        
        # 环境配置文件
        env_config = f"""# 姐妹花销售系统环境配置
# Sisters Flower Sales System Environment Configuration

# Python环境
PYTHON_VERSION={self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}
INSTALL_DIR={self.install_dir}
DATA_DIR={self.data_dir}
CONFIG_DIR={self.config_dir}
LOGS_DIR={self.logs_dir}
BACKUP_DIR={self.backup_dir}

# 系统信息
OS_NAME={self.system}
PYTHON_PATH={sys.executable}
WORKING_DIR={os.getcwd()}

# 安装时间
INSTALL_TIME={time.strftime('%Y-%m-%d %H:%M:%S')}
INSTALL_USER={getpass.getuser()}
"""
        
        env_file = self.config_dir / ".env"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_config)
        print(f"  ✅ 创建环境配置: {env_file}")
        
    def create_desktop_shortcut(self):
        """创建桌面快捷方式"""
        print("\n🖥️ 创建桌面快捷方式...")
        try:
            if self.system == "Windows":
                return self.create_windows_shortcut()
            elif self.system == "Linux":
                return self.create_linux_shortcut()
            else:
                print("  ⚠️ 不支持的操作系统，跳过快捷方式创建")
                return True
        except Exception as e:
            print(f"  ❌ 创建快捷方式失败: {e}")
            return False
            
    def create_windows_shortcut(self):
        """创建Windows快捷方式"""
        import winshell
        from win32com.client import Dispatch
        
        try:
            desktop = winshell.desktop()
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(Path(desktop) / "姐妹花销售系统.lnk"))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{self.install_dir / "enhanced_sales_system.py"}"'
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = sys.executable
            shortcut.Description = "姐妹花销售系统 - 现代化销售管理"
            shortcut.save()
            print("  ✅ Windows快捷方式创建成功")
            return True
        except Exception as e:
            print(f"  ❌ Windows快捷方式创建失败: {e}")
            return False
            
    def create_linux_shortcut(self):
        """创建Linux快捷方式"""
        try:
            desktop_file = Path.home() / "Desktop" / "sisters-flower-system.desktop"
            desktop_content = f"""[Desktop Entry]
Name=姐妹花销售系统
Name[en]=Sisters Flower Sales System
Comment=现代化销售管理系统
Comment[en]=Modern Sales Management System
Exec={sys.executable} "{self.install_dir / "enhanced_sales_system.py"}"
Icon=applications-office
Terminal=false
Type=Application
Categories=Office;
StartupNotify=true
"""
            with open(desktop_file, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            desktop_file.chmod(0o755)
            print("  ✅ Linux快捷方式创建成功")
            return True
        except Exception as e:
            print(f"  ❌ Linux快捷方式创建失败: {e}")
            return False
            
    def run_tests(self):
        """运行基本测试"""
        print("\n🧪 运行系统测试...")
        try:
            # 测试主要模块导入
            test_script = self.install_dir / "install_test.py"
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ 系统测试通过")
                return True
            else:
                print(f"  ❌ 系统测试失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ 测试运行失败: {e}")
            return False
            
    def print_completion_message(self):
        """打印完成信息"""
        print("\n" + "=" * 80)
        print("🎉 安装完成！")
        print("=" * 80)
        print("✅ 所有组件安装成功")
        print(f"📁 安装目录: {self.install_dir}")
        print(f"📊 数据库: {self.data_dir / 'sisters_flowers_system.db'}")
        print(f"⚙️ 配置文件: {self.config_dir / 'app_config.json'}")
        print(f"📋 日志文件: {self.logs_dir}")
        print("\n🚀 启动方式:")
        if self.system == "Windows":
            print("   1. 双击桌面快捷方式")
            print(f"   2. 命令行: {sys.executable} {self.install_dir / 'enhanced_sales_system.py'}")
        else:
            print(f"   1. 命令行: {sys.executable} {self.install_dir / 'enhanced_sales_system.py'}")
        print("\n📖 更多信息请查看 README.md 和用户手册")
        print("=" * 80)
        
    def run_installation(self):
        """运行完整安装流程"""
        self.print_banner()
        
        steps = [
            ("检查Python版本", self.check_python_version),
            ("创建目录结构", self.create_directories),
            ("安装依赖包", self.install_dependencies),
            ("初始化数据库", self.initialize_database),
            ("创建配置文件", self.create_config_files),
            ("创建桌面快捷方式", self.create_desktop_shortcut),
            ("运行系统测试", self.run_tests),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ 安装失败，停止在: {step_name}")
                return False
        
        self.print_completion_message()
        return True

def main():
    """主函数"""
    try:
        installer = AutoInstaller()
        return installer.run_installation()
    except KeyboardInterrupt:
        print("\n\n⚠️ 安装被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 安装过程中出现未预期错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)