#!/usr/bin/env python3
"""
姐妹花销售系统 - 系统监控和维护工具
Sisters Flower Sales System - System Monitor and Maintenance Tool

功能：
1. 系统性能监控
2. 应用状态监控
3. 数据库监控
4. 磁盘空间监控
5. 错误日志分析
6. 自动维护任务
7. 健康检查
8. 报告生成

作者: MiniMax Agent
版本: 1.0
"""

import os
import sys
import json
import sqlite3
import time
import threading
import psutil
import logging
import schedule
import smtplib
import email.mime.text
import email.mime.multipart
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import argparse
import subprocess
import shutil
import re
from email.mime.base import MIMEBase
from email import encoders
import matplotlib.pyplot as plt
import pandas as pd

class SystemMonitor:
    """系统监控类"""
    
    def __init__(self, install_dir: Path, config_file: Path):
        self.install_dir = install_dir
        self.config_file = config_file
        self.data_dir = install_dir / "data"
        self.logs_dir = install_dir / "logs"
        self.config_dir = install_dir / "config"
        
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # 监控数据存储
        self.monitor_data = {
            "cpu": [],
            "memory": [],
            "disk": [],
            "network": [],
            "database": [],
            "app_status": []
        }
        
        # 告警阈值
        self.thresholds = self.config.get("thresholds", {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "database_response_time": 5.0,
            "app_downtime": 300  # 5分钟
        })
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "monitoring": {
                "enabled": True,
                "interval_seconds": 60,
                "history_hours": 24,
                "save_history": True
            },
            "alerts": {
                "enabled": True,
                "email_enabled": False,
                "email_recipients": [],
                "smtp_server": "",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "from_email": ""
            },
            "maintenance": {
                "auto_cleanup": True,
                "cleanup_interval_days": 7,
                "database_vacuum": True,
                "vacuum_interval_days": 1
            },
            "reports": {
                "enabled": True,
                "daily_report": True,
                "weekly_report": True,
                "report_email": False
            },
            "thresholds": {
                "cpu_percent": 80.0,
                "memory_percent": 85.0,
                "disk_percent": 90.0,
                "database_response_time": 5.0,
                "app_downtime": 300
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in config[key]:
                                    config[key][subkey] = subvalue
                return config
            except Exception as e:
                print(f"加载监控配置失败，使用默认配置: {e}")
        
        return default_config
    
    def _setup_logging(self):
        """设置日志"""
        log_file = self.logs_dir / "monitor.log"
        log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # 磁盘使用情况
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            # 网络IO
            network = psutil.net_io_counters()
            
            # 进程信息
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    proc_info = proc.info
                    proc_info['uptime'] = time.time() - proc_info['create_time']
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 找出资源使用最高的进程
            top_processes = {
                "cpu": sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:5],
                "memory": sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)[:5]
            }
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                    "swap_total": swap.total,
                    "swap_percent": swap.percent
                },
                "disk": disk_usage,
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "processes": top_processes
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
            return {}
    
    def monitor_database(self) -> Dict[str, Any]:
        """监控数据库"""
        db_metrics = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "response_time": 0,
            "connections": 0,
            "table_sizes": {}
        }
        
        try:
            # 查找数据库文件
            db_files = list(self.data_dir.glob("*.db"))
            if not db_files:
                db_metrics["status"] = "no_database"
                return db_metrics
            
            db_file = db_files[0]  # 使用第一个数据库文件
            
            # 测试数据库响应时间
            start_time = time.time()
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            response_time = time.time() - start_time
            db_metrics["response_time"] = response_time
            
            # 检查数据库状态
            if response_time < self.thresholds["database_response_time"]:
                db_metrics["status"] = "healthy"
            else:
                db_metrics["status"] = "slow"
            
            # 获取表大小信息
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    # 获取表大小（通过查询页面信息）
                    cursor.execute(f"SELECT SUM(pgsize) FROM dbstat WHERE name='{table_name}'")
                    size_result = cursor.fetchone()
                    size = size_result[0] if size_result and size_result[0] else 0
                    
                    db_metrics["table_sizes"][table_name] = {
                        "row_count": count,
                        "size_bytes": size,
                        "size_mb": size / 1024 / 1024
                    }
                except sqlite3.Error:
                    continue
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"数据库监控失败: {e}")
            db_metrics["status"] = "error"
            db_metrics["error"] = str(e)
        
        return db_metrics
    
    def monitor_application(self) -> Dict[str, Any]:
        """监控应用程序"""
        app_metrics = {
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "processes": [],
            "crashes": 0,
            "uptime": 0
        }
        
        try:
            # 查找应用进程
            app_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'status']):
                try:
                    if proc.info['cmdline'] and any('enhanced_sales_system.py' in cmd for cmd in proc.info['cmdline']):
                        proc_info = {
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "status": proc.info['status'],
                            "uptime": time.time() - proc.info['create_time'],
                            "cpu_percent": proc.cpu_percent(),
                            "memory_percent": proc.memory_percent()
                        }
                        app_processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if app_processes:
                app_metrics["status"] = "running"
                app_metrics["processes"] = app_processes
                app_metrics["uptime"] = max(proc["uptime"] for proc in app_processes)
            else:
                app_metrics["status"] = "stopped"
                app_metrics["crashes"] = 1
            
        except Exception as e:
            self.logger.error(f"应用监控失败: {e}")
            app_metrics["status"] = "error"
            app_metrics["error"] = str(e)
        
        return app_metrics
    
    def check_system_health(self) -> Dict[str, Any]:
        """系统健康检查"""
        health_status = {
            "overall": "unknown",
            "components": {},
            "issues": [],
            "score": 0
        }
        
        try:
            # 系统资源检查
            metrics = self.collect_system_metrics()
            db_metrics = self.monitor_database()
            app_metrics = self.monitor_application()
            
            component_scores = []
            issues = []
            
            # CPU检查
            cpu_percent = metrics.get("cpu", {}).get("percent", 0)
            if cpu_percent < self.thresholds["cpu_percent"]:
                health_status["components"]["cpu"] = "healthy"
                component_scores.append(100)
            else:
                health_status["components"]["cpu"] = "warning"
                component_scores.append(50)
                issues.append(f"CPU使用率过高: {cpu_percent}%")
            
            # 内存检查
            memory_percent = metrics.get("memory", {}).get("percent", 0)
            if memory_percent < self.thresholds["memory_percent"]:
                health_status["components"]["memory"] = "healthy"
                component_scores.append(100)
            else:
                health_status["components"]["memory"] = "warning"
                component_scores.append(50)
                issues.append(f"内存使用率过高: {memory_percent}%")
            
            # 磁盘检查
            disk_healthy = True
            for mount, disk_info in metrics.get("disk", {}).items():
                if disk_info["percent"] > self.thresholds["disk_percent"]:
                    disk_healthy = False
                    issues.append(f"磁盘空间不足 {mount}: {disk_info['percent']:.1f}%")
            
            health_status["components"]["disk"] = "healthy" if disk_healthy else "warning"
            component_scores.append(100 if disk_healthy else 50)
            
            # 数据库检查
            db_status = db_metrics.get("status", "unknown")
            if db_status == "healthy":
                health_status["components"]["database"] = "healthy"
                component_scores.append(100)
            elif db_status == "slow":
                health_status["components"]["database"] = "warning"
                component_scores.append(70)
                issues.append("数据库响应缓慢")
            else:
                health_status["components"]["database"] = "error"
                component_scores.append(0)
                issues.append("数据库连接问题")
            
            # 应用检查
            app_status = app_metrics.get("status", "unknown")
            if app_status == "running":
                health_status["components"]["application"] = "healthy"
                component_scores.append(100)
            else:
                health_status["components"]["application"] = "error"
                component_scores.append(0)
                issues.append("应用程序未运行")
            
            # 计算总体分数和状态
            if component_scores:
                score = sum(component_scores) / len(component_scores)
                health_status["score"] = score
                
                if score >= 90:
                    health_status["overall"] = "excellent"
                elif score >= 75:
                    health_status["overall"] = "good"
                elif score >= 60:
                    health_status["overall"] = "fair"
                else:
                    health_status["overall"] = "poor"
            
            health_status["issues"] = issues
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            health_status["overall"] = "error"
            health_status["error"] = str(e)
        
        return health_status
    
    def analyze_log_errors(self, hours: int = 24) -> Dict[str, Any]:
        """分析错误日志"""
        log_analysis = {
            "timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "total_errors": 0,
            "error_types": {},
            "recent_errors": [],
            "log_files": []
        }
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # 查找日志文件
            log_patterns = ["*.log", "*error*.log", "*debug*.log"]
            log_files = []
            for pattern in log_patterns:
                log_files.extend(self.logs_dir.glob(pattern))
            
            error_patterns = [
                r'ERROR|CRITICAL|FATAL',
                r'Exception|Traceback|Error:',
                r'failed|Failed|Failure',
                r'invalid|Invalid'
            ]
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            # 检查时间戳
                            try:
                                line_time = datetime.strptime(line[:19], '%Y-%m-%d %H:%M:%S')
                                if line_time < cutoff_time:
                                    continue
                            except ValueError:
                                # 如果无法解析时间戳，假设是当前时间
                                pass
                            
                            # 检查错误模式
                            for pattern in error_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    log_analysis["total_errors"] += 1
                                    
                                    # 错误类型统计
                                    error_type = pattern.replace(r'\\', '')
                                    log_analysis["error_types"][error_type] = log_analysis["error_types"].get(error_type, 0) + 1
                                    
                                    # 最近错误（最多20条）
                                    if len(log_analysis["recent_errors"]) < 20:
                                        log_analysis["recent_errors"].append({
                                            "timestamp": line[:19] if len(line) > 19 else "",
                                            "file": log_file.name,
                                            "message": line.strip()
                                        })
                                    break
                    
                    log_analysis["log_files"].append(str(log_file))
                    
                except Exception as e:
                    self.logger.error(f"分析日志文件失败 {log_file}: {e}")
        
        except Exception as e:
            self.logger.error(f"分析错误日志失败: {e}")
        
        return log_analysis
    
    def send_alert(self, subject: str, message: str, alert_type: str = "info"):
        """发送告警"""
        if not self.config["alerts"]["enabled"]:
            return
        
        try:
            if self.config["alerts"]["email_enabled"]:
                self._send_email_alert(subject, message, alert_type)
            
            # 同时记录到日志
            log_level = logging.ERROR if alert_type == "error" else logging.WARNING
            self.logger.log(log_level, f"ALERT [{alert_type.upper()}]: {subject} - {message}")
            
        except Exception as e:
            self.logger.error(f"发送告警失败: {e}")
    
    def _send_email_alert(self, subject: str, message: str, alert_type: str):
        """发送邮件告警"""
        if not self.config["alerts"]["email_recipients"]:
            return
        
        try:
            # 创建邮件
            msg = email.mime.multipart.MIMEMultipart()
            msg['From'] = self.config["alerts"]["from_email"]
            msg['To'] = ", ".join(self.config["alerts"]["email_recipients"])
            msg['Subject'] = f"[姐妹花销售系统-{alert_type.upper()}] {subject}"
            
            # 邮件正文
            body = f"""
系统告警通知

告警类型: {alert_type.upper()}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
主题: {subject}

详细信息:
{message}

---
姐妹花销售系统监控
            """
            
            msg.attach(email.mime.text.MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.config["alerts"]["smtp_server"], self.config["alerts"]["smtp_port"])
            server.starttls()
            server.login(self.config["alerts"]["smtp_username"], self.config["alerts"]["smtp_password"])
            text = msg.as_string()
            server.sendmail(self.config["alerts"]["from_email"], self.config["alerts"]["email_recipients"], text)
            server.quit()
            
            self.logger.info(f"邮件告警已发送: {subject}")
            
        except Exception as e:
            self.logger.error(f"发送邮件告警失败: {e}")
    
    def run_maintenance_tasks(self):
        """运行维护任务"""
        self.logger.info("开始执行维护任务")
        
        try:
            # 清理日志文件
            self._cleanup_log_files()
            
            # 数据库维护
            if self.config["maintenance"]["database_vacuum"]:
                self._vacuum_database()
            
            # 清理临时文件
            self._cleanup_temp_files()
            
            # 压缩旧日志
            self._compress_old_logs()
            
            self.logger.info("维护任务完成")
            
        except Exception as e:
            self.logger.error(f"维护任务执行失败: {e}")
    
    def _cleanup_log_files(self):
        """清理日志文件"""
        try:
            retention_days = 30
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for log_file in self.logs_dir.glob("*.log*"):
                try:
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        self.logger.info(f"删除过期日志文件: {log_file}")
                except Exception as e:
                    self.logger.error(f"删除日志文件失败 {log_file}: {e}")
        except Exception as e:
            self.logger.error(f"清理日志文件失败: {e}")
    
    def _vacuum_database(self):
        """数据库整理"""
        try:
            db_files = list(self.data_dir.glob("*.db"))
            for db_file in db_files:
                conn = sqlite3.connect(str(db_file))
                conn.execute("VACUUM")
                conn.close()
                self.logger.info(f"数据库整理完成: {db_file}")
        except Exception as e:
            self.logger.error(f"数据库整理失败: {e}")
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        try:
            temp_patterns = ["*.tmp", "*.cache", "*.temp", "__pycache__"]
            for pattern in temp_patterns:
                for temp_file in self.install_dir.rglob(pattern):
                    try:
                        if temp_file.is_file():
                            temp_file.unlink()
                        elif temp_file.is_dir():
                            shutil.rmtree(temp_file)
                        self.logger.info(f"删除临时文件: {temp_file}")
                    except Exception as e:
                        self.logger.error(f"删除临时文件失败 {temp_file}: {e}")
        except Exception as e:
            self.logger.error(f"清理临时文件失败: {e}")
    
    def _compress_old_logs(self):
        """压缩旧日志"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for log_file in self.logs_dir.glob("*.log"):
                try:
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date and not log_file.name.endswith('.gz'):
                        compressed_name = f"{log_file.name}.gz"
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(log_file.parent / compressed_name, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        log_file.unlink()
                        self.logger.info(f"压缩日志文件: {compressed_name}")
                except Exception as e:
                    self.logger.error(f"压缩日志文件失败 {log_file}: {e}")
        except Exception as e:
            self.logger.error(f"压缩旧日志失败: {e}")
    
    def generate_report(self, report_type: str = "daily") -> str:
        """生成监控报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.logs_dir / f"monitor_report_{report_type}_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("姐妹花销售系统 - 监控报告\n")
                f.write("=" * 50 + "\n")
                f.write(f"报告类型: {report_type}\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                # 系统健康状态
                health = self.check_system_health()
                f.write("系统健康状态:\n")
                f.write(f"  总体状态: {health['overall']}\n")
                f.write(f"  健康分数: {health['score']:.1f}/100\n")
                f.write(f"  问题数量: {len(health['issues'])}\n")
                if health['issues']:
                    f.write("  问题列表:\n")
                    for issue in health['issues']:
                        f.write(f"    - {issue}\n")
                f.write("\n")
                
                # 系统资源使用情况
                metrics = self.collect_system_metrics()
                f.write("系统资源使用情况:\n")
                f.write(f"  CPU使用率: {metrics.get('cpu', {}).get('percent', 0):.1f}%\n")
                f.write(f"  内存使用率: {metrics.get('memory', {}).get('percent', 0):.1f}%\n")
                for mount, disk_info in metrics.get('disk', {}).items():
                    f.write(f"  磁盘使用率 ({mount}): {disk_info['percent']:.1f}%\n")
                f.write("\n")
                
                # 数据库状态
                db_metrics = self.monitor_database()
                f.write("数据库状态:\n")
                f.write(f"  状态: {db_metrics['status']}\n")
                f.write(f"  响应时间: {db_metrics['response_time']:.3f}秒\n")
                f.write(f"  表数量: {len(db_metrics['table_sizes'])}\n")
                f.write("\n")
                
                # 应用状态
                app_metrics = self.monitor_application()
                f.write("应用状态:\n")
                f.write(f"  状态: {app_metrics['status']}\n")
                f.write(f"  进程数量: {len(app_metrics['processes'])}\n")
                if app_metrics['uptime'] > 0:
                    f.write(f"  运行时间: {app_metrics['uptime']/3600:.1f}小时\n")
                f.write("\n")
                
                # 错误日志分析
                log_analysis = self.analyze_log_errors(24)
                f.write("错误日志分析 (24小时):\n")
                f.write(f"  总错误数: {log_analysis['total_errors']}\n")
                f.write(f"  错误类型:\n")
                for error_type, count in log_analysis['error_types'].items():
                    f.write(f"    {error_type}: {count}\n")
                f.write("\n")
            
            self.logger.info(f"监控报告已生成: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"生成监控报告失败: {e}")
            return ""
    
    def start_monitoring(self, continuous: bool = True):
        """开始监控"""
        self.logger.info("启动系统监控")
        
        if continuous:
            while True:
                try:
                    # 收集指标
                    metrics = self.collect_system_metrics()
                    db_metrics = self.monitor_database()
                    app_metrics = self.monitor_application()
                    
                    # 检查告警条件
                    self._check_alerts(metrics, db_metrics, app_metrics)
                    
                    # 定期运行维护任务
                    if datetime.now().hour == 2 and datetime.now().minute < 5:  # 每天凌晨2点
                        self.run_maintenance_tasks()
                    
                    # 等待下次检查
                    time.sleep(self.config["monitoring"]["interval_seconds"])
                    
                except KeyboardInterrupt:
                    self.logger.info("监控已停止")
                    break
                except Exception as e:
                    self.logger.error(f"监控过程中出现错误: {e}")
                    time.sleep(60)
        else:
            # 单次检查
            health = self.check_system_health()
            print(f"系统健康状态: {health['overall']} (分数: {health['score']:.1f})")
            if health['issues']:
                print("发现的问题:")
                for issue in health['issues']:
                    print(f"  - {issue}")
    
    def _check_alerts(self, metrics: Dict, db_metrics: Dict, app_metrics: Dict):
        """检查告警条件"""
        # CPU告警
        cpu_percent = metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.thresholds["cpu_percent"]:
            self.send_alert("CPU使用率过高", f"CPU使用率为 {cpu_percent}%", "warning")
        
        # 内存告警
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        if memory_percent > self.thresholds["memory_percent"]:
            self.send_alert("内存使用率过高", f"内存使用率为 {memory_percent}%", "warning")
        
        # 磁盘告警
        for mount, disk_info in metrics.get('disk', {}).items():
            if disk_info['percent'] > self.thresholds["disk_percent"]:
                self.send_alert("磁盘空间不足", f"{mount} 磁盘使用率为 {disk_info['percent']:.1f}%", "warning")
        
        # 数据库告警
        if db_metrics.get('status') not in ['healthy']:
            self.send_alert("数据库状态异常", f"数据库状态: {db_metrics.get('status')}", "error")
        
        # 应用告警
        if app_metrics.get('status') != 'running':
            self.send_alert("应用未运行", f"应用状态: {app_metrics.get('status')}", "error")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="姐妹花销售系统 - 系统监控工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 单次检查命令
    check_parser = subparsers.add_parser('check', help='执行单次系统检查')
    check_parser.add_argument('--health', action='store_true', help='执行健康检查')
    check_parser.add_argument('--metrics', action='store_true', help='收集系统指标')
    check_parser.add_argument('--database', action='store_true', help='监控数据库')
    check_parser.add_argument('--application', action='store_true', help='监控应用')
    check_parser.add_argument('--logs', action='store_true', help='分析错误日志')
    
    # 持续监控命令
    monitor_parser = subparsers.add_parser('monitor', help='启动持续监控')
    monitor_parser.add_argument('--interval', type=int, default=60, help='监控间隔(秒)')
    
    # 维护命令
    maintenance_parser = subparsers.add_parser('maintenance', help='执行维护任务')
    maintenance_parser.add_argument('--cleanup', action='store_true', help='清理系统')
    maintenance_parser.add_argument('--vacuum', action='store_true', help='整理数据库')
    
    # 报告命令
    report_parser = subparsers.add_parser('report', help='生成监控报告')
    report_parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], default='daily', help='报告类型')
    
    args = parser.parse_args()
    
    # 获取安装目录
    install_dir = Path(__file__).parent
    config_file = install_dir / "monitor_config.json"
    
    # 创建监控器
    monitor = SystemMonitor(install_dir, config_file)
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'check':
            if args.health:
                health = monitor.check_system_health()
                print(f"系统健康状态: {health['overall']} (分数: {health['score']:.1f})")
                if health['issues']:
                    print("发现的问题:")
                    for issue in health['issues']:
                        print(f"  - {issue}")
            elif args.metrics:
                metrics = monitor.collect_system_metrics()
                print(json.dumps(metrics, ensure_ascii=False, indent=2))
            elif args.database:
                db_metrics = monitor.monitor_database()
                print(json.dumps(db_metrics, ensure_ascii=False, indent=2))
            elif args.application:
                app_metrics = monitor.monitor_application()
                print(json.dumps(app_metrics, ensure_ascii=False, indent=2))
            elif args.logs:
                log_analysis = monitor.analyze_log_errors()
                print(json.dumps(log_analysis, ensure_ascii=False, indent=2))
            else:
                # 默认执行完整检查
                health = monitor.check_system_health()
                metrics = monitor.collect_system_metrics()
                db_metrics = monitor.monitor_database()
                app_metrics = monitor.monitor_application()
                log_analysis = monitor.analyze_log_errors()
                
                print("系统监控检查结果:")
                print(f"  健康状态: {health['overall']} (分数: {health['score']:.1f})")
                print(f"  CPU使用率: {metrics.get('cpu', {}).get('percent', 0):.1f}%")
                print(f"  内存使用率: {metrics.get('memory', {}).get('percent', 0):.1f}%")
                print(f"  数据库状态: {db_metrics.get('status', 'unknown')}")
                print(f"  应用状态: {app_metrics.get('status', 'unknown')}")
                print(f"  24小时错误数: {log_analysis.get('total_errors', 0)}")
        
        elif args.command == 'monitor':
            monitor.config["monitoring"]["interval_seconds"] = args.interval
            monitor.start_monitoring()
        
        elif args.command == 'maintenance':
            if args.cleanup:
                monitor._cleanup_log_files()
                monitor._cleanup_temp_files()
                print("系统清理完成")
            if args.vacuum:
                monitor._vacuum_database()
                print("数据库整理完成")
            if args.cleanup or args.vacuum:
                monitor.run_maintenance_tasks()
        
        elif args.command == 'report':
            report_file = monitor.generate_report(args.type)
            if report_file:
                print(f"监控报告已生成: {report_file}")
            else:
                print("生成监控报告失败")
    
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()