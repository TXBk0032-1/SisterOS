"""
配置管理模块
提供系统配置、主题、备份等配置的统一管理
"""

from .setting_manager import setting_manager
from .settings import (
    AppConfig,
    load_config,
    save_config_to_file,
    CONFIG,
    SCALE_FACTOR,
    THEME_CONFIG,
    DB_PATH
)
from .theme import (
    load_theme,
    save_theme
)

__all__ = [
    'AppConfig',
    'load_config',
    'save_config_to_file',
    'CONFIG',
    'SCALE_FACTOR',
    'THEME_CONFIG',
    'DB_PATH',
    'load_theme',
    'save_theme',
    'setting_manager'
]