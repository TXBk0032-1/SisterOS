"""
配置观察器
监听配置文件变化并支持热更新
"""

import os
import threading
import time
from typing import Callable, Dict, Any
from ..settings import AppConfig, get_config_path


class ConfigWatcher:
    """配置观察器"""
    
    def __init__(self, app_config: AppConfig, check_interval: float = 1.0):
        self.app_config = app_config
        self.check_interval = check_interval
        self._observers: Dict[str, list] = {}  # 存储观察者
        self._last_modified = {}
        self._watching = False
        self._watch_thread = None
        self._lock = threading.Lock()
    
    def add_observer(self, section: str, callback: Callable[[str, str, Any], None]):
        """添加配置观察者"""
        with self._lock:
            if section not in self._observers:
                self._observers[section] = []
            self._observers[section].append(callback)
    
    def remove_observer(self, section: str, callback: Callable):
        """移除配置观察者"""
        with self._lock:
            if section in self._observers:
                try:
                    self._observers[section].remove(callback)
                except ValueError:
                    pass
    
    def start_watching(self):
        """开始监听配置文件变化"""
        if self._watching:
            return
        
        self._watching = True
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()
    
    def stop_watching(self):
        """停止监听"""
        self._watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=2.0)
    
    def _watch_loop(self):
        """监控循环"""
        config_path = get_config_path()
        
        while self._watching:
            try:
                if os.path.exists(config_path):
                    current_modified = os.path.getmtime(config_path)
                    
                    if config_path not in self._last_modified:
                        self._last_modified[config_path] = current_modified
                    elif self._last_modified[config_path] != current_modified:
                        # 配置文件已修改，重新加载
                        self._on_config_changed(config_path)
                        self._last_modified[config_path] = current_modified
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"配置监控错误: {e}")
                time.sleep(self.check_interval)
    
    def _on_config_changed(self, config_path: str):
        """配置变更处理"""
        try:
            # 重新加载配置
            old_config = self.app_config._config.copy()
            new_config = self.app_config.load()
            
            # 对比变更并通知观察者
            self._notify_observers(old_config, new_config)
            
        except Exception as e:
            print(f"配置热更新失败: {e}")
    
    def _notify_observers(self, old_config, new_config):
        """通知观察者配置变更"""
        with self._lock:
            for section in self._observers:
                if section in old_config and section in new_config:
                    old_section = dict(old_config[section])
                    new_section = dict(new_config[section])
                    
                    # 检查每个配置项的变化
                    all_keys = set(old_section.keys()) | set(new_section.keys())
                    
                    for key in all_keys:
                        old_value = old_section.get(key)
                        new_value = new_section.get(key)
                        
                        if old_value != new_value:
                            # 通知该section的所有观察者
                            for callback in self._observers[section]:
                                try:
                                    callback(section, key, new_value)
                                except Exception as e:
                                    print(f"配置观察者执行失败: {e}")


class DynamicConfig:
    """动态配置管理器"""
    
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self._cache: Dict[str, Any] = {}
        self._watcher = ConfigWatcher(app_config)
        self._setup_observers()
    
    def _setup_observers(self):
        """设置观察者"""
        # 备份配置变更时刷新配置对象
        self._watcher.add_observer("backup", self._on_backup_config_changed)
    
    def _on_backup_config_changed(self, section: str, key: str, value: Any):
        """备份配置变更处理"""
        if key == "enabled":
            # 备份启用状态变更时，可以触发备份服务的重新配置
            print(f"备份状态已更改为: {value}")
        elif key == "interval_minutes":
            # 备份间隔变更时，可以重新计算备份时间
            print(f"备份间隔已更改为: {value} 分钟")
    
    def get_cached(self, section: str, key: str, default: Any = None) -> Any:
        """获取缓存的配置值"""
        cache_key = f"{section}.{key}"
        return self._cache.get(cache_key, default)
    
    def set_cached(self, section: str, key: str, value: Any):
        """设置缓存的配置值"""
        cache_key = f"{section}.{key}"
        self._cache[cache_key] = value
    
    def get_with_fallback(self, section: str, key: str, 
                         fallback: Any = None, 
                         cache_ttl: float = None) -> Any:
        """获取配置值，支持回退和缓存"""
        cache_key = f"{section}.{key}"
        
        # 检查缓存
        if cache_ttl is not None and cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if isinstance(cached_data, tuple) and len(cached_data) == 2:
                value, timestamp = cached_data
                if time.time() - timestamp < cache_ttl:
                    return value
        
        # 从配置获取
        value = self.app_config.get(section, key, fallback)
        
        # 缓存结果
        if cache_ttl is not None:
            self._cache[cache_key] = (value, time.time())
        else:
            self._cache[cache_key] = value
        
        return value
    
    def start_watching(self):
        """开始监听配置变化"""
        self._watcher.start_watching()
    
    def stop_watching(self):
        """停止监听配置变化"""
        self._watcher.stop_watching()
    
    def validate_all(self) -> Dict[str, bool]:
        """验证所有配置项"""
        results = {}
        
        # 验证推送配置
        try:
            endpoint = self.app_config.get("push", "endpoint", "")
            interval = self.app_config.get("push", "interval", "5")
            results["push"] = bool(endpoint) and interval.isdigit()
        except Exception:
            results["push"] = False
        
        # 验证备份配置
        try:
            backup_enabled = self.app_config.get("backup", "enabled", "false")
            interval_minutes = self.app_config.get("backup", "interval_minutes", "30")
            backup_path = self.app_config.get("backup", "path", "")
            results["backup"] = (backup_enabled.lower() in ["true", "false"] and 
                               interval_minutes.isdigit() and 
                               int(interval_minutes) > 0 and 
                               bool(backup_path))
        except Exception:
            results["backup"] = False
        
        return results
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "push": {
                "enabled": bool(self.app_config.get("push", "endpoint")),
                "endpoint": self.app_config.get("push", "endpoint"),
                "interval": self.app_config.get("push", "interval", "5")
            },
            "backup": {
                "enabled": self.app_config.get("backup", "enabled", "false"),
                "interval_minutes": self.app_config.get("backup", "interval_minutes", "30"),
                "path": self.app_config.get("backup", "path")
            },
            "database": {
                "last_push_table": self.app_config.get("database", "last_push_table")
            }
        }


# 创建全局动态配置实例
import time
_app_config = AppConfig()
_dynamic_config = DynamicConfig(_app_config)
_dynamic_config.start_watching()
