"""
应用配置管理
统一的配置加载、保存和验证机制
"""

import os
import sys
import configparser
from typing import Dict, Any
from pathlib import Path

# 全局配置变量
CONFIG = None
SCALE_FACTOR = 1.3

# 配置文件名
THEME_CONFIG = "theme_config.txt"
DB_PATH = os.path.join(os.path.dirname(sys.argv[0]), 'sisters_flowers.db')


class AppConfig:
    """应用配置类"""
    
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config_path = self._get_config_path()
        
    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的EXE环境
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "config.ini")
    
    def load(self) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        config_path = self._config_path
        
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(config_path):
            self._create_default_config(config)
            self.save(config)
        
        config.read(config_path, encoding='utf-8')
        self._config = config
        return config
    
    def _create_default_config(self, config: configparser.ConfigParser):
        """创建默认配置"""
        # 推送配置
        config["push"] = {
            "interval": "5",
            "endpoint": "https://58e4706c.tw.cpolar.io/pushdata"
        }
        
        # 数据库配置
        config["database"] = {
            "last_push_table": "push_status"
        }
        
        # 备份配置
        config["backup"] = {
            "enabled": "false",
            "time": "03:00",
            "interval_minutes": "30",
            "path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        }
    
    def save(self, config: configparser.ConfigParser = None) -> bool:
        """保存配置到文件"""
        try:
            if config is None:
                config = self._config
            
            with open(self._config_path, "w", encoding="utf-8") as f:
                config.write(f)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """获取配置值"""
        if self._config is None:
            self.load()
        return self._config.get(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str) -> bool:
        """设置配置值"""
        if self._config is None:
            self.load()
        
        if not self._config.has_section(section):
            self._config.add_section(section)
        
        self._config.set(section, key, value)
        return self.save()
    
    def get_section(self, section: str) -> Dict[str, str]:
        """获取整个配置节"""
        if self._config is None:
            self.load()
        
        if self._config.has_section(section):
            return dict(self._config[section])
        return {}
    
    def validate(self) -> bool:
        """验证配置的有效性"""
        try:
            # 验证推送配置
            if not self._config.has_section("push"):
                return False
            
            # 验证备份配置
            if not self._config.has_section("backup"):
                return False
            
            # 验证间隔时间
            interval = self.get("backup", "interval_minutes", "30")
            if not interval.isdigit() or int(interval) <= 0:
                return False
            
            return True
        except Exception:
            return False


def load_config() -> configparser.ConfigParser:
    """加载配置文件（兼容性函数）"""
    global CONFIG
    if CONFIG is None:
        app_config = AppConfig()
        CONFIG = app_config.load()
    return CONFIG


def save_config_to_file() -> bool:
    """保存配置到文件（兼容性函数）"""
    global CONFIG
    if CONFIG is None:
        return False
    
    try:
        config_path = get_config_path()
        with open(config_path, "w", encoding="utf-8") as f:
            CONFIG.write(f)
        print("配置已成功保存到文件")
        return True
    except Exception as e:
        print(f"保存配置文件失败: {str(e)}")
        return False


def get_config_path() -> str:
    """获取配置文件的绝对路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的EXE环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "config.ini")


def resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径（适配开发环境和打包后环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后的EXE环境
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# 全局配置实例
_app_config = AppConfig()
CONFIG = _app_config.load()
