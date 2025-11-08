"""
数据库管理器
负责数据库连接、初始化和事务管理
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional, Dict, Any, List

from ..config.settings import DB_PATH


class DatabaseManager:
    """数据库管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.db_path = DB_PATH
        self._local = threading.local()
    
    @contextmanager
    def get_connection(self, timeout: float = 30.0):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            if hasattr(self._local, 'connection'):
                conn = self._local.connection
            else:
                conn = sqlite3.connect(
                    self.db_path, 
                    timeout=timeout, 
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                self._local.connection = conn
            
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            # 不在这里关闭连接，让连接保持在本地线程中
            pass
    
    @contextmanager
    def get_cursor(self, timeout: float = 30.0):
        """获取数据库游标的上下文管理器"""
        with self.get_connection(timeout) as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def execute(self, sql: str, params: tuple = (), timeout: float = 30.0) -> int:
        """执行SQL语句，返回受影响的行数"""
        with self.get_cursor(timeout) as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount
    
    def execute_many(self, sql: str, params_list: List[tuple], timeout: float = 30.0) -> int:
        """批量执行SQL语句"""
        with self.get_cursor(timeout) as cursor:
            cursor.executemany(sql, params_list)
            return cursor.rowcount
    
    def fetch_one(self, sql: str, params: tuple = (), timeout: float = 30.0) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        with self.get_cursor(timeout) as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, sql: str, params: tuple = (), timeout: float = 30.0) -> List[Dict[str, Any]]:
        """获取所有记录"""
        with self.get_cursor(timeout) as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def fetch_many(self, sql: str, params: tuple = (), limit: int = 100, timeout: float = 30.0) -> List[Dict[str, Any]]:
        """获取多条记录"""
        with self.get_cursor(timeout) as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchmany(limit)
            return [dict(row) for row in rows]
    
    def execute_script(self, script: str, timeout: float = 30.0):
        """执行SQL脚本"""
        with self.get_cursor(timeout) as cursor:
            cursor.executescript(script)
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息"""
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_tables(self) -> List[str]:
        """获取所有表名"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """检查列是否存在"""
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {row['name'] for row in cursor.fetchall()}
            return column_name in columns
    
    def add_column(self, table_name: str, column_name: str, column_type: str) -> bool:
        """添加列"""
        try:
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            self.execute(sql)
            return True
        except Exception:
            return False
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')
    
    def vacuum(self):
        """清理数据库"""
        with self.get_cursor() as cursor:
            cursor.execute("VACUUM")
    
    def backup(self, backup_path: str) -> bool:
        """备份数据库"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception:
            return False
    
    def restore(self, backup_path: str) -> bool:
        """恢复数据库"""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception:
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()
