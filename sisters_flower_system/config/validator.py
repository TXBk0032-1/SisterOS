"""
配置验证器
负责验证配置的有效性和完整性
"""

import re
import os
from typing import Dict, List, Any, Optional, Tuple
from .settings import AppConfig


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.validation_rules = {
            "push": {
                "endpoint": self._validate_url,
                "interval": self._validate_positive_int
            },
            "backup": {
                "enabled": self._validate_boolean,
                "time": self._validate_time_format,
                "interval_minutes": self._validate_positive_int,
                "path": self._validate_directory_path
            },
            "database": {
                "last_push_table": self._validate_table_name
            }
        }
        
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """验证所有配置项"""
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # 验证各个配置节
        for section, rules in self.validation_rules.items():
            if self.app_config._config.has_section(section):
                for key, validator in rules.items():
                    if self.app_config._config.has_option(section, key):
                        value = self.app_config.get(section, key)
                        is_valid, error_msg = validator(key, value)
                        
                        if not is_valid:
                            self.validation_errors.append(f"[{section}.{key}] {error_msg}")
                        elif error_msg:
                            self.validation_warnings.append(f"[{section}.{key}] {error_msg}")
            else:
                self.validation_errors.append(f"配置节 [{section}] 不存在")
        
        # 执行跨配置项验证
        self._validate_cross_config()
        
        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_url(self, key: str, value: str) -> Tuple[bool, Optional[str]]:
        """验证URL格式"""
        if not value:
            return False, "URL不能为空"
        
        # 简单的URL格式验证
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(value):
            return False, "URL格式不正确"
        
        return True, None
    
    def _validate_positive_int(self, key: str, value: str) -> Tuple[bool, Optional[str]]:
        """验证正整数"""
        try:
            int_value = int(value)
            if int_value <= 0:
                return False, "必须为正整数"
            return True, None
        except ValueError:
            return False, "必须为整数"
    
    def _validate_boolean(self, key: str, value: str) -> Tuple[bool, Optional[str]]:
        """验证布尔值"""
        if value.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
            return True, None
        return False, "必须是 true/false 或 1/0"
    
    def _validate_time_format(self, key: str, value: str) -> Tuple[bool, Optional[str]]:
        """验证时间格式 HH:MM"""
        if not value:
            return False, "时间不能为空"
        
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        if not time_pattern.match(value):
            return False, "时间格式必须为 HH:MM (如 03:00)"
        
        return True, None
    
    def _validate_directory_path(self, key: str, value: str) -> Tuple[bool, Optional[str]]:
        """验证目录路径"""
        if not value:
            return False, "路径不能为空"
        
        # 检查路径是否有效
        try:
            # 尝试创建目录以检查权限
            os.makedirs(value, exist_ok=True)
            return True, None
        except PermissionError:
            return False, "没有权限访问该路径"
        except OSError as e:
            return False, f"路径无效: {str(e)}"
    
    def _validate_table_name(self, key: str, value: str) -> Tuple[bool, Optional[str]]:
        """验证表名"""
        if not value:
            return False, "表名不能为空"
        
        # 表名不能包含特殊字符
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            return False, "表名只能包含字母、数字和下划线，且不能以数字开头"
        
        return True, None
    
    def _validate_cross_config(self):
        """执行跨配置项验证"""
        # 验证备份时间和间隔的逻辑关系
        try:
            backup_time = self.app_config.get("backup", "time", "")
            interval_minutes = int(self.app_config.get("backup", "interval_minutes", "30"))
            
            if backup_time and interval_minutes < 60:
                self.validation_warnings.append(
                    "[backup] 备份间隔小于1小时，可能会影响性能"
                )
        except (ValueError, TypeError):
            pass
        
        # 验证推送间隔和备份间隔的关系
        try:
            push_interval = int(self.app_config.get("push", "interval", "5"))
            backup_interval = int(self.app_config.get("backup", "interval_minutes", "30"))
            
            if push_interval >= backup_interval:
                self.validation_warnings.append(
                    "[push/backup] 推送间隔不应该大于或等于备份间隔"
                )
        except (ValueError, TypeError):
            pass
    
    def fix_common_issues(self) -> List[str]:
        """修复常见的配置问题"""
        fixes_applied = []
        
        # 修复布尔值格式
        backup_enabled = self.app_config.get("backup", "enabled", "false")
        if backup_enabled.lower() not in ['true', 'false']:
            if backup_enabled in ['1', 'yes', 'on']:
                self.app_config.set("backup", "enabled", "true")
                fixes_applied.append("备份启用状态已标准化为 true/false")
            elif backup_enabled in ['0', 'no', 'off']:
                self.app_config.set("backup", "enabled", "false")
                fixes_applied.append("备份启用状态已标准化为 true/false")
        
        # 修复路径格式
        backup_path = self.app_config.get("backup", "path", "")
        if backup_path and not os.path.isabs(backup_path):
            # 转换为绝对路径
            import sys
            base_path = os.path.dirname(sys.argv[0])
            abs_path = os.path.join(base_path, backup_path)
            self.app_config.set("backup", "path", abs_path)
            fixes_applied.append("备份路径已转换为绝对路径")
        
        # 保存修复后的配置
        if fixes_applied:
            self.app_config.save()
        
        return fixes_applied
    
    def get_validation_report(self) -> str:
        """获取验证报告"""
        is_valid, errors, warnings = self.validate_all()
        
        report = []
        report.append("=== 配置验证报告 ===")
        report.append(f"验证时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"配置状态: {'✅ 有效' if is_valid else '❌ 无效'}")
        report.append("")
        
        if errors:
            report.append("❌ 错误:")
            for error in errors:
                report.append(f"  • {error}")
            report.append("")
        
        if warnings:
            report.append("⚠️ 警告:")
            for warning in warnings:
                report.append(f"  • {warning}")
            report.append("")
        
        if not errors and not warnings:
            report.append("✅ 所有配置项都有效")
        
        return "\n".join(report)
    
    def auto_fix_and_validate(self) -> Tuple[bool, str]:
        """自动修复并验证配置"""
        # 先尝试自动修复
        fixes = self.fix_common_issues()
        
        # 重新验证
        is_valid, errors, warnings = self.validate_all()
        
        report_parts = []
        
        if fixes:
            report_parts.append("已应用的修复:")
            for fix in fixes:
                report_parts.append(f"  • {fix}")
            report_parts.append("")
        
        # 重新获取验证结果
        is_valid, errors, warnings = self.validate_all()
        
        if errors:
            report_parts.append("仍存在的错误:")
            for error in errors:
                report_parts.append(f"  • {error}")
        
        if warnings:
            report_parts.append("警告:")
            for warning in warnings:
                report_parts.append(f"  • {warning}")
        
        if not errors and not warnings:
            report_parts.append("✅ 配置验证通过")
        
        return is_valid, "\n".join(report_parts)


class ConfigHealthChecker:
    """配置健康检查器"""
    
    def __init__(self, app_config: AppConfig):
        self.app_config = app_config
        self.validator = ConfigValidator(app_config)
    
    def check_config_health(self) -> Dict[str, Any]:
        """检查配置健康状况"""
        health_report = {
            "overall_status": "unknown",
            "score": 0,
            "issues": [],
            "recommendations": [],
            "last_check": __import__('datetime').datetime.now().isoformat()
        }
        
        is_valid, errors, warnings = self.validator.validate_all()
        
        # 计算健康分数
        total_checks = len(errors) + len(warnings)
        if total_checks == 0:
            health_report["overall_status"] = "excellent"
            health_report["score"] = 100
            health_report["issues"] = []
            health_report["recommendations"] = ["配置状态良好"]
        elif len(errors) == 0:
            health_report["overall_status"] = "good"
            health_report["score"] = 80
            health_report["issues"] = warnings
            health_report["recommendations"] = ["配置基本有效，但有改进空间"]
        else:
            health_report["overall_status"] = "poor"
            health_report["score"] = max(0, 100 - len(errors) * 20 - len(warnings) * 10)
            health_report["issues"] = errors + warnings
            health_report["recommendations"] = ["需要修复配置错误以确保系统正常运行"]
        
        return health_report
