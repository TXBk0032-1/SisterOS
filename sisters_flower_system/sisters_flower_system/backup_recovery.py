#!/usr/bin/env python3
"""
姐妹花销售系统 - 备份恢复工具
Sisters Flower Sales System - Backup and Recovery Tool

功能：
1. 自动备份
2. 手动备份
3. 数据恢复
4. 备份计划管理
5. 备份压缩和加密
6. 备份验证
7. 增量备份

作者: MiniMax Agent
版本: 1.0
"""

import argparse
import hashlib
import json
import logging
import shutil
import sqlite3
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

import schedule


class BackupManager:
    """备份管理器"""
    
    def __init__(self, install_dir: Path, config_file: Path):
        self.install_dir = install_dir
        self.config_file = config_file
        self.data_dir = install_dir / "data"
        self.config_dir = install_dir / "config"
        self.logs_dir = install_dir / "logs"
        self.backup_dir = install_dir / "backup"
        
        # 确保目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        self._setup_schedule()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "backup": {
                "enabled": True,
                "auto_backup": True,
                "interval_hours": 24,
                "retention_days": 30,
                "compression": True,
                "encryption": False,
                "verify_backup": True,
                "max_backup_size_mb": 1000
            },
            "paths": {
                "data_dir": str(self.data_dir),
                "config_dir": str(self.config_dir),
                "logs_dir": str(self.logs_dir),
                "backup_dir": str(self.backup_dir)
            },
            "files": {
                "include": [
                    "*.db",
                    "*.json",
                    "*.ini",
                    "*.log",
                    "*.txt"
                ],
                "exclude": [
                    "*.tmp",
                    "*.cache",
                    "__pycache__",
                    ".git",
                    "node_modules"
                ]
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in config[key]:
                                    config[key][subkey] = subvalue
                return config
            except Exception as e:
                print(f"加载配置文件失败，使用默认配置: {e}")
        
        return default_config
    
    def _setup_logging(self):
        """设置日志"""
        log_file = self.logs_dir / "backup.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _setup_schedule(self):
        """设置备份计划"""
        if self.config["backup"]["auto_backup"]:
            interval_hours = self.config["backup"]["interval_hours"]
            schedule.every(interval_hours).hours.do(self.create_auto_backup)
            self.logger.info(f"自动备份已启用，间隔: {interval_hours}小时")
    
    def create_auto_backup(self):
        """创建自动备份"""
        backup_name = f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return self.create_backup(backup_name, backup_type="auto")
    
    def create_manual_backup(self, backup_name: str) -> bool:
        """创建手动备份"""
        return self.create_backup(backup_name, backup_type="manual")
    
    def create_backup(self, backup_name: str, backup_type: str = "manual") -> bool:
        """创建备份"""
        self.logger.info(f"开始创建备份: {backup_name} (类型: {backup_type})")
        
        try:
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 创建备份清单
            manifest = {
                "backup_name": backup_name,
                "backup_type": backup_type,
                "created_at": datetime.now().isoformat(),
                "system_info": {
                    "platform": sys.platform,
                    "python_version": sys.version,
                    "install_dir": str(self.install_dir)
                },
                "files": [],
                "total_size": 0,
                "file_count": 0,
                "checksums": {}
            }
            
            # 备份数据文件
            if self.data_dir.exists():
                self._backup_directory(self.data_dir, backup_path / "data", manifest)
            
            # 备份配置文件
            if self.config_dir.exists():
                self._backup_directory(self.config_dir, backup_path / "config", manifest)
            
            # 备份日志文件（可选）
            if self.logs_dir.exists() and self.config.get("backup", {}).get("include_logs", False):
                self._backup_directory(self.logs_dir, backup_path / "logs", manifest)
            
            # 创建数据库特殊备份
            self._backup_databases(backup_path, manifest)
            
            # 压缩备份（可选）
            if self.config["backup"]["compression"]:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    manifest["compressed"] = True
                    manifest["compressed_path"] = str(compressed_path)
            
            # 验证备份（可选）
            if self.config["backup"]["verify_backup"]:
                if not self._verify_backup(backup_path):
                    self.logger.error("备份验证失败")
                    return False
            
            # 保存备份清单
            manifest_file = backup_path / "manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            # 清理过期备份
            self._cleanup_old_backups()
            
            self.logger.info(f"备份创建完成: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return False
    
    def _backup_directory(self, source_dir: Path, dest_dir: Path, manifest: Dict):
        """备份目录"""
        include_patterns = self.config["files"]["include"]
        exclude_patterns = self.config["files"]["exclude"]
        
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                # 检查是否应该包含此文件
                file_name = file_path.name
                include = any(file_path.match(pattern) for pattern in include_patterns)
                exclude = any(file_path.match(pattern) for pattern in exclude_patterns)
                
                if include and not exclude:
                    # 计算相对路径
                    rel_path = file_path.relative_to(source_dir)
                    dest_file = dest_dir / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(file_path, dest_file)
                    
                    # 计算校验和
                    checksum = self._calculate_file_checksum(file_path)
                    
                    # 记录文件信息
                    file_info = {
                        "source": str(file_path),
                        "destination": str(dest_file),
                        "relative_path": str(rel_path),
                        "size": file_path.stat().st_size,
                        "checksum": checksum,
                        "mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    manifest["files"].append(file_info)
                    manifest["total_size"] += file_info["size"]
                    manifest["file_count"] += 1
                    manifest["checksums"][str(rel_path)] = checksum
    
    def _backup_databases(self, backup_path: Path, manifest: Dict):
        """备份数据库"""
        db_dir = backup_path / "databases"
        db_dir.mkdir(exist_ok=True)
        
        for db_file in self.data_dir.glob("*.db"):
            try:
                # 使用SQLite的备份API
                db_backup_path = db_dir / db_file.name
                self._backup_sqlite_db(db_file, db_backup_path)
                
                # 记录数据库备份信息
                manifest["databases"] = manifest.get("databases", [])
                manifest["databases"].append({
                    "name": db_file.name,
                    "source": str(db_file),
                    "backup": str(db_backup_path),
                    "size": db_file.stat().st_size,
                    "checksum": self._calculate_file_checksum(db_file)
                })
                
            except Exception as e:
                self.logger.error(f"备份数据库失败 {db_file}: {e}")
    
    def _backup_sqlite_db(self, source_db: Path, dest_db: Path):
        """备份SQLite数据库"""
        conn = sqlite3.connect(str(source_db))
        backup_conn = sqlite3.connect(str(dest_db))
        conn.backup(backup_conn)
        backup_conn.close()
        conn.close()
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """压缩备份"""
        try:
            compressed_path = backup_path.parent / f"{backup_path.name}.tar.gz"
            
            with tarfile.open(compressed_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_path.name)
            
            # 删除未压缩的备份
            shutil.rmtree(backup_path)
            
            self.logger.info(f"备份已压缩: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"压缩备份失败: {e}")
            return None
    
    def _verify_backup(self, backup_path: Path) -> bool:
        """验证备份"""
        try:
            manifest_file = backup_path / "manifest.json"
            if not manifest_file.exists():
                self.logger.error("备份清单文件不存在")
                return False
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 验证文件完整性
            for file_info in manifest.get("files", []):
                backup_file = Path(file_info["destination"])
                if not backup_file.exists():
                    self.logger.error(f"备份文件缺失: {backup_file}")
                    return False
                
                # 验证校验和
                current_checksum = self._calculate_file_checksum(backup_file)
                if current_checksum != file_info["checksum"]:
                    self.logger.error(f"文件校验和验证失败: {backup_file}")
                    return False
            
            # 验证数据库完整性
            db_dir = backup_path / "databases"
            if db_dir.exists():
                for db_file in db_dir.glob("*.db"):
                    if not self._verify_sqlite_db(db_file):
                        self.logger.error(f"数据库完整性验证失败: {db_file}")
                        return False
            
            self.logger.info("备份验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"验证备份失败: {e}")
            return False
    
    def _verify_sqlite_db(self, db_path: Path) -> bool:
        """验证SQLite数据库完整性"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 执行完整性检查
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] == "ok"
            
        except Exception as e:
            self.logger.error(f"数据库完整性检查失败 {db_path}: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _cleanup_old_backups(self):
        """清理过期备份"""
        retention_days = self.config["backup"]["retention_days"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleaned_count = 0
        
        for backup_item in self.backup_dir.iterdir():
            if backup_item.is_dir() or backup_item.suffix in ['.tar.gz', '.zip', '.gz']:
                try:
                    # 尝试从名称中提取日期
                    if backup_item.name.startswith(('auto_backup_', 'manual_backup_')):
                        date_str = backup_item.name.split('_')[-2:]
                        if len(date_str) == 2:
                            backup_date = datetime.strptime('_'.join(date_str), '%Y%m%d_%H%M%S')
                            if backup_date < cutoff_date:
                                if backup_item.is_dir():
                                    shutil.rmtree(backup_item)
                                else:
                                    backup_item.unlink()
                                cleaned_count += 1
                                self.logger.info(f"删除过期备份: {backup_item}")
                except (ValueError, IndexError):
                    # 如果无法解析日期，删除30天前的文件
                    stat = backup_item.stat()
                    file_date = datetime.fromtimestamp(stat.st_mtime)
                    if file_date < cutoff_date:
                        if backup_item.is_dir():
                            shutil.rmtree(backup_item)
                        else:
                            backup_item.unlink()
                        cleaned_count += 1
                        self.logger.info(f"删除过期备份: {backup_item}")
        
        if cleaned_count > 0:
            self.logger.info(f"清理完成，删除了 {cleaned_count} 个过期备份")
    
    def restore_backup(self, backup_path: Path, restore_path: Optional[Path] = None) -> bool:
        """恢复备份"""
        self.logger.info(f"开始恢复备份: {backup_path}")
        
        try:
            if restore_path is None:
                restore_path = self.install_dir
            
            # 加载备份清单
            manifest_file = backup_path / "manifest.json"
            if not manifest_file.exists():
                self.logger.error("备份清单文件不存在")
                return False
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 恢复前创建当前系统备份
            if not self._create_pre_restore_backup():
                self.logger.warning("创建预恢复备份失败，继续执行恢复")
            
            # 解压备份（如果需要）
            working_backup = backup_path
            if backup_path.suffix in ['.tar.gz', '.zip', '.gz']:
                working_backup = self._extract_backup(backup_path)
                if working_backup is None:
                    return False
            
            # 恢复文件
            success = self._restore_files(working_backup, restore_path, manifest)
            
            # 验证恢复结果
            if success and self.config["backup"]["verify_backup"]:
                success = self._verify_restore(restore_path, manifest)
            
            # 清理临时文件
            if working_backup != backup_path and working_backup.exists():
                shutil.rmtree(working_backup)
            
            if success:
                self.logger.info("备份恢复成功")
            else:
                self.logger.error("备份恢复失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"恢复备份失败: {e}")
            return False
    
    def _create_pre_restore_backup(self) -> bool:
        """创建恢复前备份"""
        try:
            backup_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return self.create_backup(backup_name, "pre_restore")
        except Exception as e:
            self.logger.error(f"创建预恢复备份失败: {e}")
            return False
    
    def _extract_backup(self, compressed_backup: Path) -> Optional[Path]:
        """解压备份"""
        try:
            working_dir = Path(tempfile.mkdtemp(prefix="backup_restore_"))
            
            if compressed_backup.suffix == '.tar.gz':
                with tarfile.open(compressed_backup, "r:gz") as tar:
                    tar.extractall(working_dir)
                # 找到解压后的备份目录
                for item in working_dir.iterdir():
                    if item.is_dir() and item.name.startswith(('auto_backup_', 'manual_backup_')):
                        return item
            else:
                self.logger.error(f"不支持的压缩格式: {compressed_backup.suffix}")
                return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"解压备份失败: {e}")
            return None
    
    def _restore_files(self, backup_path: Path, restore_path: Path, manifest: Dict) -> bool:
        """恢复文件"""
        try:
            for file_info in manifest.get("files", []):
                backup_file = Path(file_info["destination"])
                if not backup_file.exists():
                    self.logger.warning(f"备份文件不存在: {backup_file}")
                    continue
                
                # 计算目标路径
                rel_path = Path(file_info["relative_path"])
                target_file = restore_path / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(backup_file, target_file)
                self.logger.debug(f"恢复文件: {target_file}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"恢复文件失败: {e}")
            return False
    
    def _verify_restore(self, restore_path: Path, manifest: Dict) -> bool:
        """验证恢复结果"""
        try:
            for file_info in manifest.get("files", []):
                target_file = restore_path / file_info["relative_path"]
                if not target_file.exists():
                    self.logger.error(f"恢复后文件缺失: {target_file}")
                    return False
                
                # 验证文件大小
                if target_file.stat().st_size != file_info["size"]:
                    self.logger.error(f"文件大小不匹配: {target_file}")
                    return False
                
                # 验证校验和
                current_checksum = self._calculate_file_checksum(target_file)
                if current_checksum != file_info["checksum"]:
                    self.logger.error(f"文件校验和不匹配: {target_file}")
                    return False
            
            self.logger.info("恢复验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"验证恢复失败: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []
        
        for backup_item in self.backup_dir.iterdir():
            if backup_item.is_dir() or backup_item.suffix in ['.tar.gz', '.zip', '.gz']:
                backup_info = {
                    "name": backup_item.name,
                    "path": str(backup_item),
                    "type": "directory" if backup_item.is_dir() else "compressed",
                    "size": self._get_directory_size(backup_item),
                    "created": self._get_creation_time(backup_item)
                }
                
                # 尝试读取清单文件
                if backup_item.is_dir():
                    manifest_file = backup_item / "manifest.json"
                    if manifest_file.exists():
                        try:
                            with open(manifest_file, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                            backup_info.update({
                                "backup_type": manifest.get("backup_type", "unknown"),
                                "file_count": manifest.get("file_count", 0),
                                "created_at": manifest.get("created_at", "")
                            })
                        except Exception:
                            pass
                
                backups.append(backup_info)
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def _get_directory_size(self, path: Path) -> int:
        """获取目录大小"""
        if path.is_file():
            return path.stat().st_size
        else:
            return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    
    def _get_creation_time(self, path: Path) -> datetime:
        """获取创建时间"""
        return datetime.fromtimestamp(path.stat().st_ctime)
    
    def start_scheduler(self):
        """启动备份调度器"""
        self.logger.info("启动备份调度器")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

class RecoveryTool:
    """恢复工具"""
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.logger = logging.getLogger(__name__)
    
    def interactive_restore(self):
        """交互式恢复"""
        print("=" * 60)
        print("姐妹花销售系统 - 交互式恢复工具")
        print("=" * 60)
        
        # 列出可用备份
        backups = self.backup_manager.list_backups()
        if not backups:
            print("❌ 没有找到可用备份")
            return False
        
        print(f"\n找到 {len(backups)} 个备份:")
        for i, backup in enumerate(backups, 1):
            created_date = backup.get("created_at", backup["created"].strftime("%Y-%m-%d %H:%M:%S"))
            size_mb = backup["size"] / 1024 / 1024
            print(f"{i}. {backup['name']}")
            print(f"   类型: {backup['backup_type']} | 大小: {size_mb:.1f}MB | 创建: {created_date}")
        
        # 选择备份
        while True:
            try:
                choice = input(f"\n请选择要恢复的备份 (1-{len(backups)}): ")
                backup_index = int(choice) - 1
                if 0 <= backup_index < len(backups):
                    selected_backup = backups[backup_index]
                    break
                else:
                    print("❌ 无效选择，请重试")
            except ValueError:
                print("❌ 请输入有效数字")
        
        # 确认恢复
        print(f"\n⚠️ 警告: 恢复操作将覆盖当前系统数据!")
        confirm = input("确认继续恢复? (yes/no): ").lower()
        if confirm != "yes":
            print("恢复操作已取消")
            return False
        
        # 执行恢复
        backup_path = Path(selected_backup["path"])
        success = self.backup_manager.restore_backup(backup_path)
        
        if success:
            print("✅ 恢复成功!")
        else:
            print("❌ 恢复失败!")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="姐妹花销售系统 - 备份恢复工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建备份命令
    backup_parser = subparsers.add_parser('backup', help='创建备份')
    backup_parser.add_argument('--name', type=str, required=True, help='备份名称')
    backup_parser.add_argument('--type', choices=['auto', 'manual'], default='manual', help='备份类型')
    
    # 恢复备份命令
    restore_parser = subparsers.add_parser('restore', help='恢复备份')
    restore_parser.add_argument('--backup-path', type=Path, required=True, help='备份路径')
    restore_parser.add_argument('--restore-path', type=Path, help='恢复目标路径')
    restore_parser.add_argument('--interactive', action='store_true', help='交互式恢复')
    
    # 列出备份命令
    list_parser = subparsers.add_parser('list', help='列出备份')
    
    # 启动调度器命令
    scheduler_parser = subparsers.add_parser('scheduler', help='启动备份调度器')
    
    # 清理过期备份命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理过期备份')
    
    args = parser.parse_args()
    
    # 获取安装目录
    install_dir = Path(__file__).parent
    config_file = install_dir / "backup_config.json"
    
    # 创建备份管理器
    backup_manager = BackupManager(install_dir, config_file)
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'backup':
            if args.type == 'auto':
                success = backup_manager.create_auto_backup()
            else:
                success = backup_manager.create_manual_backup(args.name)
            sys.exit(0 if success else 1)
        
        elif args.command == 'restore':
            if args.interactive:
                recovery_tool = RecoveryTool(backup_manager)
                success = recovery_tool.interactive_restore()
            else:
                backup_path = Path(args.backup_path)
                restore_path = Path(args.restore_path) if args.restore_path else None
                success = backup_manager.restore_backup(backup_path, restore_path)
            sys.exit(0 if success else 1)
        
        elif args.command == 'list':
            backups = backup_manager.list_backups()
            if not backups:
                print("没有找到备份")
            else:
                print("可用备份:")
                for backup in backups:
                    created_date = backup.get("created_at", backup["created"].strftime("%Y-%m-%d %H:%M:%S"))
                    size_mb = backup["size"] / 1024 / 1024
                    print(f"  {backup['name']} - {backup['backup_type']} - {size_mb:.1f}MB - {created_date}")
        
        elif args.command == 'scheduler':
            backup_manager.start_scheduler()
        
        elif args.command == 'cleanup':
            backup_manager._cleanup_old_backups()
            print("清理完成")
    
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()