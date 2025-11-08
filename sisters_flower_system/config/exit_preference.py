"""
退出偏好设置管理
处理程序退出时的偏好设置（最小化到系统托盘或直接退出）
"""

import os
import configparser
from ..settings import resource_path


def save_exit_preference(choice: str, remember: bool) -> bool:
    """保存退出偏好设置"""
    try:
        config_path = resource_path("exit_preference.ini")
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if not config.has_section("Exit"):
            config.add_section("Exit")
        
        config.set("Exit", "choice", choice)  # "exit" 或 "tray"
        config.set("Exit", "remember", str(remember))
        
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"保存退出偏好失败: {e}")
        return False


def load_exit_preference() -> tuple:
    """加载退出偏好设置"""
    try:
        config_path = resource_path("exit_preference.ini")
        if not os.path.exists(config_path):
            return None, False
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if not config.has_section("Exit"):
            return None, False
        
        choice = config.get("Exit", "choice", fallback=None)
        remember = config.getboolean("Exit", "remember", fallback=False)
        return choice, remember
    except Exception as e:
        print(f"加载退出偏好失败: {e}")
        return None, False


def reset_exit_preference() -> bool:
    """重置退出偏好设置"""
    try:
        config_path = resource_path("exit_preference.ini")
        if os.path.exists(config_path):
            os.remove(config_path)
        return True
    except Exception as e:
        print(f"重置退出偏好失败: {e}")
        return False
