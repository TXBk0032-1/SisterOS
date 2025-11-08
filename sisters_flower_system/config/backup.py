"""
备份配置管理
处理数据库备份的相关配置和操作
"""

import os
import shutil
from datetime import datetime
from typing import Optional
from .settings import CONFIG, resource_path


class BackupConfig:
    """备份配置类"""
    
    def __init__(self):
        self.enabled = False
        self.time = "03:00"
        self.interval_minutes = 30
        self.path = ""
        self._load_from_config()
    
    def _load_from_config(self):
        """从配置文件加载备份设置"""
        try:
            self.enabled = CONFIG.get("backup", "enabled", fallback="false").lower() == "true"
            self.time = CONFIG.get("backup", "time", fallback="03:00")
            self.interval_minutes = int(CONFIG.get("backup", "interval_minutes", fallback="30"))
            self.path = CONFIG.get("backup", "path", fallback="")
            
            # 如果路径为空，使用默认路径
            if not self.path:
                base_path = os.path.dirname(sys.argv[0])
                self.path = os.path.join(base_path, "backups")
        except Exception as e:
            print(f"加载备份配置失败: {e}")
    
    def save_to_config(self):
        """保存备份设置到配置文件"""
        try:
            CONFIG.set("backup", "enabled", "true" if self.enabled else "false")
            CONFIG.set("backup", "time", self.time)
            CONFIG.set("backup", "interval_minutes", str(self.interval_minutes))
            CONFIG.set("backup", "path", os.path.abspath(self.path))
            
            from .settings import save_config_to_file
            return save_config_to_file()
        except Exception as e:
            print(f"保存备份配置失败: {e}")
            return False
    
    def validate(self) -> bool:
        """验证备份配置的有效性"""
        try:
            # 验证时间格式（HH:MM）
            if ":" not in self.time:
                return False
            hour, minute = self.time.split(":")
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                return False
            
            # 验证间隔时间
            if self.interval_minutes <= 0:
                return False
            
            # 验证路径
            if not self.path:
                return False
            
            return True
        except Exception:
            return False


class BackupManager:
    """备份管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.config = BackupConfig()
    
    def create_backup(self) -> Optional[str]:
        """创建数据库备份"""
        try:
            backup_path = self.config.path
            if not backup_path:
                return None
            
            # 确保备份目录存在
            os.makedirs(backup_path, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"backup_{timestamp}.db")
            
            # 执行备份
            shutil.copy2(self.db_path, backup_file)
            
            print(f"[{datetime.now().strftime('%Y.%m.%d %H:%M:%S')}] 自动备份成功：{backup_file}")
            return backup_file
            
        except Exception as e:
            error_msg = f"[{datetime.now().strftime('%Y.%m.%d %H:%M:%S')}] 自动备份失败：{str(e)}"
            print(error_msg)
            return None
    
    def restore_backup(self, backup_file: str) -> bool:
        """从备份恢复数据库"""
        try:
            if not os.path.exists(backup_file):
                print(f"备份文件不存在: {backup_file}")
                return False
            
            # 先备份当前数据
            temp_backup = f"{self.db_path}.temp_backup"
            shutil.copy2(self.db_path, temp_backup)
            
            try:
                # 执行恢复
                shutil.copy2(backup_file, self.db_path)
                print(f"数据库恢复成功: {backup_file}")
                
                # 删除临时备份
                if os.path.exists(temp_backup):
                    os.remove(temp_backup)
                
                return True
                
            except Exception as e:
                # 恢复失败则回滚到临时备份
                shutil.copy2(temp_backup, self.db_path)
                if os.path.exists(temp_backup):
                    os.remove(temp_backup)
                raise e
                
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def list_backups(self) -> list:
        """列出所有备份文件"""
        try:
            backup_path = self.config.path
            if not os.path.exists(backup_path):
                return []
            
            backup_files = []
            for file in os.listdir(backup_path):
                if file.startswith("backup_") and file.endswith(".db"):
                    file_path = os.path.join(backup_path, file)
                    stat = os.stat(file_path)
                    backup_files.append({
                        "file": file,
                        "path": file_path,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime),
                        "modified": datetime.fromtimestamp(stat.st_mtime)
                    })
            
            # 按创建时间倒序排列
            backup_files.sort(key=lambda x: x["created"], reverse=True)
            return backup_files
            
        except Exception as e:
            print(f"列出备份文件失败: {e}")
            return []
    
    def cleanup_old_backups(self, keep_count: int = 30) -> int:
        """清理旧备份，只保留指定数量"""
        try:
            backup_files = self.list_backups()
            if len(backup_files) <= keep_count:
                return 0
            
            # 删除多余的备份文件
            files_to_delete = backup_files[keep_count:]
            deleted_count = 0
            
            for backup in files_to_delete:
                try:
                    os.remove(backup["path"])
                    deleted_count += 1
                except Exception as e:
                    print(f"删除备份文件失败 {backup['file']}: {e}")
            
            print(f"清理了 {deleted_count} 个旧备份文件")
            return deleted_count
            
        except Exception as e:
            print(f"清理旧备份失败: {e}")
            return 0
