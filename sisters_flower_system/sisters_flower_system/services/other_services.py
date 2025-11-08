"""
其他服务
包含NFC、节日计算、销售目标、数据推送、备份等功能
"""

import base64
import json
import os
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class NFCService:
    """NFC卡操作服务"""
    
    def __init__(self):
        self.key_path = os.path.join(os.path.dirname(__file__), 'nfc_key.bin')
        self._monitoring = False
        self._monitor_thread = None
    
    def generate_key(self, force: bool = False):
        """生成加密密钥"""
        if os.path.exists(self.key_path) and not force:
            return self.load_key()
        key = AESGCM.generate_key(bit_length=256)
        with open(self.key_path, 'wb') as f:
            f.write(key)
        try:
            os.chmod(self.key_path, 0o600)
        except Exception:
            pass
        return key
    
    def load_key(self):
        """加载加密密钥"""
        if not os.path.exists(self.key_path):
            return self.generate_key()
        with open(self.key_path, 'rb') as f:
            return f.read()
    
    def encrypt_credentials(self, username: str, password: str, key=None) -> Dict[str, Any]:
        """加密用户凭据"""
        if key is None:
            key = self.load_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        payload = json.dumps({"u": username, "p": password}, ensure_ascii=False).encode('utf-8')
        ct = aesgcm.encrypt(nonce, payload, None)
        blob = nonce + ct
        return {"v":1, "type":"login", "data": base64.b64encode(blob).decode('ascii')}
    
    def start_monitoring(self, callback=None):
        """开始NFC监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, args=(callback,), daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """停止NFC监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self, callback):
        """监控循环"""
        while self._monitoring:
            try:
                # 这里可以添加实际的NFC监控逻辑
                if callback:
                    callback("NFC: 监控中...")
                time.sleep(2)
            except Exception as e:
                if callback:
                    callback(f"NFC: 错误 - {str(e)}")
                time.sleep(2)


class FestivalService:
    """节日计算服务"""
    
    def get_today_festival(self) -> Optional[Dict[str, str]]:
        """获取今日节日信息"""
        from ..utils.system_utils import check_festival
        return check_festival()


class GoalService:
    """销售目标服务"""
    
    def __init__(self):
        from ..database.repositories import SalesRepository
        from ..config.settings import DB_PATH
        self.sales_repo = SalesRepository()
        self.db_path = DB_PATH
    
    def get_current_goals(self) -> Dict[str, float]:
        """获取当前销售目标"""
        from datetime import date
        today = date.today()
        day_key = today.strftime("%Y-%m-%d")
        month_key = today.strftime("%Y-%m")
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 获取今日目标
        cur.execute("SELECT target_value FROM sales_goals WHERE goal_type = 'day' AND goal_key = ?", (day_key,))
        day_result = cur.fetchone()
        day_goal = day_result[0] if day_result else 1000.0
        
        # 获取本月目标
        cur.execute("SELECT target_value FROM sales_goals WHERE goal_type = 'month' AND goal_key = ?", (month_key,))
        month_result = cur.fetchone()
        month_goal = month_result[0] if month_result else 30000.0
        
        conn.close()
        return day_goal, month_goal
    
    def set_goals(self, day_goal: float, month_goal: float):
        """设置销售目标"""
        from datetime import date
        today = date.today()
        day_key = today.strftime("%Y-%m-%d")
        month_key = today.strftime("%Y-%m")
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 设置今日目标
        cur.execute(
            "INSERT OR REPLACE INTO sales_goals (goal_type, goal_key, target_value, created_at) VALUES (?, ?, ?, ?)",
            ("day", day_key, day_goal, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        # 设置本月目标
        cur.execute(
            "INSERT OR REPLACE INTO sales_goals (goal_type, goal_key, target_value, created_at) VALUES (?, ?, ?, ?)",
            ("month", month_key, month_goal, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
    
    def get_progress(self) -> Dict[str, Any]:
        """获取销售进度"""
        day_goal, month_goal = self.get_current_goals()
        
        from datetime import date
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        month_str = today.strftime("%Y-%m")
        
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 获取今日销售额
        cur.execute("SELECT SUM(total_paid) FROM sales WHERE datetime LIKE ?", (f"{date_str}%",))
        day_result = cur.fetchone()
        day_current = day_result[0] if day_result and day_result[0] else 0
        
        # 获取本月销售额
        cur.execute("SELECT SUM(total_paid) FROM sales WHERE datetime LIKE ?", (f"{month_str}%",))
        month_result = cur.fetchone()
        month_current = month_result[0] if month_result and month_result[0] else 0
        
        conn.close()
        
        # 计算完成百分比
        day_percentage = (day_current / day_goal * 100) if day_goal > 0 else 0
        month_percentage = (month_current / month_goal * 100) if month_goal > 0 else 0
        
        return {
            "day_progress": {
                "current": day_current, 
                "goal": day_goal, 
                "percentage": round(day_percentage, 2)
            },
            "month_progress": {
                "current": month_current, 
                "goal": month_goal, 
                "percentage": round(month_percentage, 2)
            }
        }


class PushService:
    """数据推送服务"""
    
    def push_all_data(self) -> bool:
        """推送所有数据"""
        try:
            import requests
            from ..database.manager import db_manager
            from ..config.settings import CONFIG
            
            # 获取数据
            sales = db_manager.fetch_all("SELECT * FROM sales")
            inventory = db_manager.fetch_all("SELECT * FROM inventory")
            
            # 构造负载
            payload = {
                "sales": sales,
                "inventory": inventory,
                "push_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 发送请求
            push_url = CONFIG.get("push", "endpoint")
            if push_url:
                response = requests.post(push_url, json=payload, timeout=10)
                return response.status_code == 200
            
        except Exception as e:
            print(f"推送数据失败: {e}")
        return False
    
    def push_sales_data(self, date_str: str = None) -> bool:
        """推送指定日期的销售数据"""
        try:
            import requests
            from ..database.manager import db_manager
            from ..config.settings import CONFIG
            
            if not date_str:
                date_str = date.today().strftime("%Y-%m-%d")
            
            # 获取指定日期的销售数据
            sales = db_manager.fetch_all(
                "SELECT * FROM sales WHERE datetime LIKE ?", 
                (f"{date_str}%",)
            )
            
            payload = {
                "date": date_str,
                "sales": sales,
                "push_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            push_url = CONFIG.get("push", "sales_endpoint")
            if push_url:
                response = requests.post(push_url, json=payload, timeout=10)
                return response.status_code == 200
            
        except Exception as e:
            print(f"推送销售数据失败: {e}")
        return False


class BackupService:
    """备份服务"""
    
    def __init__(self):
        from ..config.backup import BackupManager
        from ..config.settings import DB_PATH
        self.manager = BackupManager(DB_PATH)
    
    def create_backup(self) -> Optional[str]:
        """创建备份"""
        return self.manager.create_backup()
    
    def restore_backup(self, backup_file: str) -> bool:
        """恢复备份"""
        return self.manager.restore_backup(backup_file)
