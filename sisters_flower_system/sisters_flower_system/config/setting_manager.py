#!/usr/bin/env python3
"""
设置配置文件管理
管理 setting.json 中的用户设置数据
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path


class SettingManager:
    """设置管理类"""
    
    def __init__(self, setting_file: str = "settings.json"):
        self.setting_file = setting_file
        self._settings = self._load_settings()
    
    def _get_setting_path(self) -> str:
        """获取设置文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的EXE环境
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "config", self.setting_file)
    
    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        setting_path = self._get_setting_path()
        if os.path.exists(setting_path):
            try:
                with open(setting_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载设置文件失败: {e}")
        
        # 返回默认设置
        return self._get_default_settings()
    
    def _save_settings(self) -> bool:
        """保存设置"""
        setting_path = self._get_setting_path()
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(setting_path), exist_ok=True)
            
            with open(setting_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置文件失败: {e}")
            return False
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """获取默认设置"""
        return {
            "appearance": {
                "theme_mode": "light",  # light, dark, auto
                "primary_color": "#0067C0",  # Win11 蓝色
                "secondary_color": "#A4D5FF",  # Win11 浅蓝
                "accent_color": "#4CC2FF",  # Win11 亮蓝
                "background_color": "#FFFFFF",  # 纯白背景
                "text_color": "#000000",  # 纯黑文字
                "use_system_theme": False,
                "window_transparency": 1.0,
                "animations_enabled": True,
                "font_size": "normal",  # small, normal, large
                "corner_radius": 8
            },
            "behavior": {
                "auto_save": True,
                "auto_backup": True,
                "backup_interval": 24,  # 小时
                "confirm_deletions": True,
                "show_tooltips": True,
                "sound_effects": True,
                "shortcuts_enabled": True
            },
            "dashboard": {
                "refresh_interval": 30,  # 秒
                "show_charts": True,
                "chart_type": "line",  # line, bar, pie
                "default_period": "week",  # day, week, month, year
                "kpi_cards": [
                    "total_sales",
                    "total_members", 
                    "inventory_alerts",
                    "profit_margin"
                ]
            },
            "data_export": {
                "default_format": "xlsx",  # xlsx, csv, pdf
                "include_charts": True,
                "date_range": "month",
                "auto_export": False,
                "export_path": ""
            },
            "notifications": {
                "enabled": True,
                "low_stock_threshold": 10,
                "member_birthday_reminder": True,
                "daily_summary": True,
                "goal_achievement": True
            },
            "security": {
                "require_password": False,
                "session_timeout": 30,  # 分钟
                "audit_log": True,
                "data_encryption": False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """设置值（支持点号分隔的嵌套键）"""
        keys = key.split('.')
        current = self._settings
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # 设置值
        current[keys[-1]] = value
        return self._save_settings()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有设置"""
        return self._settings.copy()
    
    def update(self, data: Dict[str, Any]) -> bool:
        """批量更新设置"""
        def deep_update(target: Dict, source: Dict):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    deep_update(target[key], value)
                else:
                    target[key] = value
        
        deep_update(self._settings, data)
        return self._save_settings()
    
    def reset_to_default(self) -> bool:
        """重置为默认设置"""
        self._settings = self._get_default_settings()
        return self._save_settings()
    
    def export_settings(self, export_path: str) -> bool:
        """导出设置到文件"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """从文件导入设置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            self._settings = imported_settings
            return self._save_settings()
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False


# 全局设置管理器实例
setting_manager = SettingManager()