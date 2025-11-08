"""
路径工具模块
提供路径相关的工具函数
"""

import os
import sys
from pathlib import Path
from typing import Union


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径
    适配开发环境和打包后环境
    """
    if getattr(sys, 'frozen', False):
        # 打包后的EXE环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent
    return os.path.join(base_path, relative_path)

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent

def get_database_path(db_name: str = "sisters_flowers.db") -> str:
    """获取数据库文件路径"""
    return get_resource_path(db_name)

def ensure_directory(path: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_icon_path(icon_name: str) -> str:
    """获取图标文件路径"""
    icons_dir = get_resource_path("assets/icons")
    return os.path.join(icons_dir, icon_name)

def get_config_path(config_name: str = "config.ini") -> str:
    """获取配置文件路径"""
    return get_resource_path(f"config/{config_name}")

def get_logs_dir() -> Path:
    """获取日志目录"""
    return ensure_directory(get_resource_path("logs"))

def get_exports_dir() -> Path:
    """获取导出文件目录"""
    return ensure_directory(get_resource_path("exports"))

def get_temp_dir() -> Path:
    """获取临时文件目录"""
    return ensure_directory(get_resource_path("temp"))

def normalize_path(path: Union[str, Path]) -> str:
    """标准化路径格式"""
    return os.path.normpath(str(path))

def is_valid_path(path: Union[str, Path]) -> bool:
    """检查路径是否有效"""
    try:
        Path(path).resolve()
        return True
    except (OSError, ValueError):
        return False

def join_path(*paths) -> str:
    """连接路径"""
    return os.path.join(*paths)

def get_relative_path(path: Union[str, Path], base: Union[str, Path] = None) -> str:
    """获取相对路径"""
    if base is None:
        base = get_project_root()
    return os.path.relpath(path, base)

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()

def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）"""
    return os.path.getsize(file_path)

def is_file_exists(file_path: Union[str, Path]) -> bool:
    """检查文件是否存在"""
    return os.path.isfile(file_path)

def is_directory_exists(dir_path: Union[str, Path]) -> bool:
    """检查目录是否存在"""
    return os.path.isdir(dir_path)


# 导出所有公共函数
__all__ = [
    'get_resource_path',
    'get_project_root', 
    'get_database_path',
    'ensure_directory',
    'get_icon_path',
    'get_config_path',
    'get_logs_dir',
    'get_exports_dir',
    'get_temp_dir',
    'normalize_path',
    'is_valid_path',
    'join_path',
    'get_relative_path',
    'get_file_extension',
    'get_file_size',
    'is_file_exists',
    'is_directory_exists'
]