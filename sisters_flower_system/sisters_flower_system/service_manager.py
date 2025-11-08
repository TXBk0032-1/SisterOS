#!/usr/bin/env python3
"""
姐妹花销售系统 - 服务管理工具
Sisters Flower Sales System - Service Management Tool

功能：
1. 系统服务安装/卸载
2. 服务启动/停止/重启
3. 服务状态监控
4. 性能监控
5. 自动备份服务
6. 日志管理

作者: MiniMax Agent
版本: 1.0
"""

import os
import sys
import time
import json
import sqlite3
import threading
import schedule
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import argparse
import signal
import shutil

class ServiceManager:
    """服务管理器类"""
    
    def __init__(self):
        self.system = self._get_system_type()
        self.install_dir = Path(__file__).parent
        self.config_dir = self.install_dir / "config"
        self.data_dir = self.install_dir / "data"
        self.logs_dir = self.install_dir / "logs"
        self.backup_dir = self.install_dir / "backup"
        
        # 服务配置
        self.service_config = {
            "name": "SistersFlowerSales",
            "display_name": "姐妹花销售系统",
            "description": "姐妹花销售系统后台服务",
            "working_directory": str(self.install_dir),
            "executable": sys.executable,
            "script": str(self.install_dir / "enhanced_sales_system.py")
        }
        
        # 监控配置
        self.monitor_config = {
            "cpu_threshold": 80.0,  # CPU使用率阈值
            "memory_threshold": 85.0,  # 内存使用率阈值
            "disk_threshold": 90.0,  # 磁盘使用率阈值
            "log_level": "INFO"
        }
        
        self._setup_logging()
        
    def _get_system_type(self) -> str:
        """获取系统类型"""
        if sys.platform.startswith('win'):
            return 'Windows'
        elif sys.platform.startswith('linux'):
            return 'Linux'
        elif sys.platform.startswith('darwin'):
            return 'macOS'
        else:
            return 'Unknown'
    
    def _setup_logging(self):
        """设置日志"""
        self.logs_dir.mkdir(exist_ok=True)
        log_file = self.logs_dir / "service_manager.log"
        
        logging.basicConfig(
            level=getattr(logging, self.monitor_config["log_level"]),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def install_service(self) -> bool:
        """安装系统服务"""
        self.logger.info("开始安装系统服务...")
        
        try:
            if self.system == 'Windows':
                return self._install_windows_service()
            elif self.system == 'Linux':
                return self._install_linux_service()
            else:
                self.logger.error(f"不支持的系统: {self.system}")
                return False
        except Exception as e:
            self.logger.error(f"安装服务失败: {e}")
            return False
    
    def _install_windows_service(self) -> bool:
        """安装Windows服务"""
        try:
            # 创建服务安装脚本
            install_script = self.install_dir / "install_windows_service.py"
            service_code = f'''import win32serviceutil
import win32service
import win32event
import win32evtlogutil
import servicemanager
import sys
import os

class SistersFlowerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "{self.service_config["name"]}"
    _svc_display_name_ = "{self.service_config["display_name"]}"
    _svc_description_ = "{self.service_config["description"]}"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.PYS_SERVICE_STARTED,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        # 启动主应用程序
        import subprocess
        import sys
        from pathlib import Path
        
        app_path = Path(r"{self.service_config["script"]}")
        working_dir = Path(r"{self.service_config["working_directory"]}")
        
        while True:
            try:
                # 检查应用是否运行
                proc = subprocess.Popen([
                    sys.executable, str(app_path)
                ], cwd=str(working_dir))
                
                # 等待进程结束
                proc.wait()
                
                # 如果进程异常退出，等待5秒后重启
                if proc.returncode != 0:
                    time.sleep(5)
                    
            except Exception as e:
                servicemanager.LogErrorMsg(f"Service error: {{e}}")
                time.sleep(10)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SistersFlowerService)
'''
            
            with open(install_script, 'w', encoding='utf-8') as f:
                f.write(service_code)
            
            # 安装服务
            result = subprocess.run([
                sys.executable, str(install_script), 'install', '--interactive=stop'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Windows服务安装成功")
                return True
            else:
                self.logger.error(f"Windows服务安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"安装Windows服务失败: {e}")
            return False
    
    def _install_linux_service(self) -> bool:
        """安装Linux服务"""
        try:
            # 创建systemd服务文件
            service_file = Path("/etc/systemd/system/sisters-flower-sales.service")
            service_content = f'''[Unit]
Description={self.service_config["display_name"]}
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={self.service_config["working_directory"]}
ExecStart={self.service_config["executable"]} {self.service_config["script"]}
Restart=always
RestartSec=10
StandardOutput=append:{self.logs_dir}/service.log
StandardError=append:{self.logs_dir}/service_error.log

[Install]
WantedBy=multi-user.target
'''
            
            # 写入服务文件（需要root权限）
            if os.geteuid() == 0:
                with open(service_file, 'w') as f:
                    f.write(service_content)
                
                # 重新加载systemd并启用服务
                subprocess.run(['systemctl', 'daemon-reload'], check=True)
                subprocess.run(['systemctl', 'enable', 'sisters-flower-sales'], check=True)
                self.logger.info("Linux服务安装成功")
                return True
            else:
                self.logger.error("安装Linux服务需要root权限")
                return False
                
        except Exception as e:
            self.logger.error(f"安装Linux服务失败: {e}")
            return False
    
    def start_service(self) -> bool:
        """启动服务"""
        self.logger.info("启动服务...")
        
        try:
            if self.system == 'Windows':
                result = subprocess.run([
                    'net', 'start', self.service_config["name"]
                ], capture_output=True, text=True)
            else:
                result = subprocess.run([
                    'systemctl', 'start', 'sisters-flower-sales'
                ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("服务启动成功")
                return True
            else:
                self.logger.error(f"服务启动失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"启动服务失败: {e}")
            return False
    
    def stop_service(self) -> bool:
        """停止服务"""
        self.logger.info("停止服务...")
        
        try:
            if self.system == 'Windows':
                result = subprocess.run([
                    'net', 'stop', self.service_config["name"]
                ], capture_output=True, text=True)
            else:
                result = subprocess.run([
                    'systemctl', 'stop', 'sisters-flower-sales'
                ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("服务停止成功")
                return True
            else:
                self.logger.error(f"服务停止失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"停止服务失败: {e}")
            return False
    
    def restart_service(self) -> bool:
        """重启服务"""
        self.logger.info("重启服务...")
        
        if self.stop_service() and self.start_service():
            self.logger.info("服务重启成功")
            return True
        else:
            self.logger.error("服务重启失败")
            return False
    
    def get_service_status(self) -> Dict[str, any]:
        """获取服务状态"""
        try:
            if self.system == 'Windows':
                result = subprocess.run([
                    'sc', 'query', self.service_config["name"]
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    output = result.stdout
                    if 'RUNNING' in output:
                        status = 'running'
                    elif 'STOPPED' in output:
                        status = 'stopped'
                    else:
                        status = 'unknown'
                else:
                    status = 'not_installed'
                    
            else:
                result = subprocess.run([
                    'systemctl', 'is-active', 'sisters-flower-sales'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    if result.stdout.strip() == 'active':
                        status = 'running'
                    else:
                        status = 'stopped'
                else:
                    status = 'not_installed'
            
            return {
                "status": status,
                "service_name": self.service_config["name"],
                "system": self.system,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取服务状态失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def uninstall_service(self) -> bool:
        """卸载服务"""
        self.logger.info("卸载服务...")
        
        try:
            if self.system == 'Windows':
                result = subprocess.run([
                    sys.executable, 'install_windows_service.py', 'remove', '--interactive=stop'
                ], cwd=str(self.install_dir), capture_output=True, text=True)
            else:
                if os.geteuid() == 0:
                    subprocess.run(['systemctl', 'stop', 'sisters-flower-sales'], check=True)
                    subprocess.run(['systemctl', 'disable', 'sisters-flower-sales'], check=True)
                    service_file = Path("/etc/systemd/system/sisters-flower-sales.service")
                    if service_file.exists():
                        service_file.unlink()
                    subprocess.run(['systemctl', 'daemon-reload'], check=True)
                else:
                    self.logger.error("卸载Linux服务需要root权限")
                    return False
            
            if result.returncode == 0 if 'result' in locals() else True:
                self.logger.info("服务卸载成功")
                return True
            else:
                self.logger.error(f"服务卸载失败: {result.stderr if 'result' in locals() else 'Unknown error'}")
                return False
                
        except Exception as e:
            self.logger.error(f"卸载服务失败: {e}")
            return False

class SystemMonitor:
    """系统监控类"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """开始系统监控"""
        if self.monitoring:
            self.logger.warning("监控已在运行")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("系统监控已启动")
    
    def stop_monitoring(self):
        """停止系统监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("系统监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 监控CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > self.service_manager.monitor_config["cpu_threshold"]:
                    self.logger.warning(f"CPU使用率过高: {cpu_percent}%")
                
                # 监控内存使用率
                memory = psutil.virtual_memory()
                if memory.percent > self.service_manager.monitor_config["memory_threshold"]:
                    self.logger.warning(f"内存使用率过高: {memory.percent}%")
                
                # 监控磁盘使用率
                disk = psutil.disk_usage(str(self.service_manager.install_dir))
                if (disk.percent > self.service_manager.monitor_config["disk_threshold"]):
                    self.logger.warning(f"磁盘使用率过高: {disk.percent}%")
                
                # 检查应用进程
                self._check_application_process()
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                self.logger.error(f"监控过程中出现错误: {e}")
                time.sleep(60)
    
    def _check_application_process(self):
        """检查应用进程状态"""
        try:
            process_found = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'enhanced_sales_system.py' in ' '.join(proc.info['cmdline'] or []):
                        process_found = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not process_found:
                self.logger.warning("检测到主应用进程未运行，尝试重启...")
                self.service_manager.start_service()
                
        except Exception as e:
            self.logger.error(f"检查应用进程失败: {e}")

class BackupService:
    """备份服务类"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
    def create_backup(self) -> bool:
        """创建系统备份"""
        self.logger.info("开始创建系统备份...")
        
        try:
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.service_manager.backup_dir / f"backup_{backup_time}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 备份数据库
            db_file = self.service_manager.data_dir / "sisters_flowers_system.db"
            if db_file.exists():
                shutil.copy2(db_file, backup_path / "database.db")
                self.logger.info("数据库备份完成")
            
            # 备份配置文件
            config_files = list(self.service_manager.config_dir.glob("*.json"))
            config_files += list(self.service_manager.config_dir.glob("*.ini"))
            for config_file in config_files:
                shutil.copy2(config_file, backup_path / config_file.name)
            self.logger.info("配置文件备份完成")
            
            # 备份用户数据
            user_data_files = list(self.service_manager.data_dir.glob("*"))
            for data_file in user_data_files:
                if data_file.name != "sisters_flowers_system.db":
                    if data_file.is_file():
                        shutil.copy2(data_file, backup_path / data_file.name)
                    elif data_file.is_dir():
                        shutil.copytree(data_file, backup_path / data_file.name, dirs_exist_ok=True)
            self.logger.info("用户数据备份完成")
            
            # 创建备份清单
            backup_manifest = {
                "backup_time": datetime.now().isoformat(),
                "backup_path": str(backup_path),
                "files": [f.name for f in backup_path.rglob("*") if f.is_file()],
                "size_mb": sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file()) / 1024 / 1024
            }
            
            with open(backup_path / "manifest.json", 'w', encoding='utf-8') as f:
                json.dump(backup_manifest, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"系统备份完成: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return False
    
    def cleanup_old_backups(self, retention_days: int = 30):
        """清理旧备份"""
        self.logger.info("开始清理旧备份...")
        
        try:
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            cleaned_count = 0
            
            for backup_dir in self.service_manager.backup_dir.glob("backup_*"):
                if backup_dir.is_dir():
                    # 检查备份时间
                    try:
                        backup_time = datetime.strptime(backup_dir.name, "backup_%Y%m%d_%H%M%S")
                        if backup_time < cutoff_time:
                            shutil.rmtree(backup_dir)
                            cleaned_count += 1
                            self.logger.info(f"删除旧备份: {backup_dir}")
                    except ValueError:
                        continue
            
            self.logger.info(f"清理完成，删除了 {cleaned_count} 个旧备份")
            return True
            
        except Exception as e:
            self.logger.error(f"清理旧备份失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="姐妹花销售系统 - 服务管理工具")
    parser.add_argument("action", choices=["install", "uninstall", "start", "stop", "restart", "status", "monitor", "backup"], 
                       help="要执行的操作")
    parser.add_argument("--daemon", action="store_true", help="后台运行模式")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔（秒）")
    
    args = parser.parse_args()
    
    service_manager = ServiceManager()
    
    try:
        if args.action == "install":
            service_manager.install_service()
        elif args.action == "uninstall":
            service_manager.uninstall_service()
        elif args.action == "start":
            service_manager.start_service()
        elif args.action == "stop":
            service_manager.stop_service()
        elif args.action == "restart":
            service_manager.restart_service()
        elif args.action == "status":
            status = service_manager.get_service_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        elif args.action == "monitor":
            monitor = SystemMonitor(service_manager)
            if args.daemon:
                monitor.start_monitoring()
                try:
                    while True:
                        time.sleep(args.interval)
                except KeyboardInterrupt:
                    monitor.stop_monitoring()
            else:
                # 一次性监控
                status = service_manager.get_service_status()
                print(f"服务状态: {status['status']}")
                
                # 显示系统资源使用情况
                print(f"CPU使用率: {psutil.cpu_percent()}%")
                memory = psutil.virtual_memory()
                print(f"内存使用率: {memory.percent}%")
                disk = psutil.disk_usage(str(service_manager.install_dir))
                print(f"磁盘使用率: {disk.percent}%")
        elif args.action == "backup":
            backup_service = BackupService(service_manager)
            backup_service.create_backup()
            backup_service.cleanup_old_backups()
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"操作失败: {e}")

if __name__ == "__main__":
    main()