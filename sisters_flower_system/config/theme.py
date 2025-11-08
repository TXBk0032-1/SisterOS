"""
主题配置管理
处理界面主题的保存、加载和应用
"""

import os
from ..settings import resource_path


def load_theme() -> str:
    """加载并返回上次保存的主题"""
    try:
        theme_path = resource_path(THEME_CONFIG)
        if os.path.exists(theme_path):
            with open(theme_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception as e:
        print(f"加载主题失败: {e}")
    return None


def save_theme(theme_name: str) -> bool:
    """保存当前主题"""
    try:
        theme_path = resource_path(THEME_CONFIG)
        with open(theme_path, 'w', encoding='utf-8') as f:
            f.write(theme_name)
        return True
    except Exception as e:
        print(f"保存主题失败: {e}")
        return False


def get_available_themes() -> list:
    """获取可用主题列表"""
    try:
        from ttkbootstrap import Style
        style = Style()
        return list(style.theme_names())
    except Exception:
        return ["litera", "minty", "pulse", "lumen", "journal", "simplex"]


def get_theme_translations() -> dict:
    """获取主题名称汉化映射"""
    return {
        "litera": "蓝色(推荐)",
        "minty": "绿色(推荐)",
        "pulse": "紫色",
        "lumen": "青色",
        "journal": "橙色",
        "simplex": "红色",
        "flatly": "灰色",
        "cerculean": "浅蓝色",
        "cosmo": "暗蓝色",
        "sandstone": "暗青色",
        "yeti": "深青色",
        "united": "天空蓝(有背景不好看)",
        "morph": "蓝色(有背景不好看)",
        "darkly": "暗黑色(有背景不好看)",
        "superhero": "暗蓝色(有背景不好看)",
        "solar": "暗黄色(有背景不好看)",
        "cyborg": "反转(有背景不好看)",
        "vapor": "暗紫色(有背景不好看)",
    }


def translate_theme(theme_name: str) -> str:
    """将主题名翻译为中文"""
    translations = get_theme_translations()
    return translations.get(theme_name, theme_name)


def reverse_translate_theme(chinese_name: str) -> str:
    """将中文主题名翻译回英文"""
    translations = get_theme_translations()
    reverse_translations = {v: k for k, v in translations.items()}
    return reverse_translations.get(chinese_name, chinese_name)
