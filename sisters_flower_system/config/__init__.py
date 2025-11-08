"""
配置管理模块
提供系统配置、主题、备份等配置的统一管理
"""

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

from .exit_preference import (
    save_exit_preference,
    load_exit_preference,
    reset_exit_preference
)

from .backup import (
    BackupConfig,
    BackupManager
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
    'save_exit_preference',
    'load_exit_preference',
    'reset_exit_preference',
    'BackupConfig',
    'BackupManager'
]