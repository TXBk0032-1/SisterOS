"""
数据库初始化
负责创建和管理数据库表结构
"""

import sqlite3
from datetime import date, datetime
from .manager import db_manager
from ..config.settings import CONFIG


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.db = db_manager
    
    def initialize(self):
        """初始化或升级数据库结构"""
        # 初始化各个表
        self._create_users_table()
        self._create_members_table()
        self._create_inventory_table()
        self._create_sales_table()
        self._create_sale_items_table()
        self._create_memory_reminder_table()
        self._create_push_status_table()
        self._create_sales_goals_table()
        
        # 检查并插入默认数据
        self._insert_default_data()
        
        # 处理数据库升级
        self._handle_upgrades()
    
    def _create_users_table(self):
        """创建用户表"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            avatar TEXT
        )
        """
        self.db.execute_script(sql)
        
        # 检查是否已有avatar字段
        if not self.db.column_exists("users", "avatar"):
            self.db.add_column("users", "avatar", "TEXT")
            # 为现有用户设置默认头像
            self.db.execute("UPDATE users SET avatar = 'profile_photo.png' WHERE avatar IS NULL")
    
    def _create_members_table(self):
        """创建会员表"""
        sql = """
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            balance REAL DEFAULT 0,
            remark TEXT,
            join_date TEXT
        )
        """
        self.db.execute_script(sql)
        
        # 检查是否已有join_date字段
        if not self.db.column_exists("members", "join_date"):
            self.db.add_column("members", "join_date", "TEXT")
            # 为现有会员设置默认日期
            self.db.execute("UPDATE members SET join_date = datetime('now', 'localtime') WHERE join_date IS NULL")
    
    def _create_inventory_table(self):
        """创建商品库存表"""
        sql = """
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT UNIQUE,
            price REAL DEFAULT 0,
            member_price REAL DEFAULT 0,
            remark TEXT
        )
        """
        self.db.execute_script(sql)
        
        # 检查并移除stock字段（如果存在）
        if self.db.column_exists("inventory", "stock"):
            self._migrate_inventory_table()
    
    def _create_sales_table(self):
        """创建销售表"""
        sql = """
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            total_due REAL NOT NULL,
            total_paid REAL NOT NULL,
            is_member INTEGER NOT NULL DEFAULT 0
        )
        """
        self.db.execute_script(sql)
        
        # 检查是否已有member_phone字段
        if not self.db.column_exists("sales", "member_phone"):
            self.db.add_column("sales", "member_phone", "TEXT")
    
    def _create_sale_items_table(self):
        """创建销售明细表"""
        sql = """
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            category TEXT,
            name TEXT,
            price REAL,
            quantity INTEGER,
            remark TEXT,
            FOREIGN KEY(sale_id) REFERENCES sales(sale_id)
        )
        """
        self.db.execute_script(sql)
        
        # 检查是否已有remark字段
        if not self.db.column_exists("sale_items", "remark"):
            self.db.add_column("sale_items", "remark", "TEXT")
    
    def _create_memory_reminder_table(self):
        """创建内存提醒表"""
        sql = """
        CREATE TABLE IF NOT EXISTS memory_reminder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_reminder_date TEXT NOT NULL,
            reminder_interval INTEGER NOT NULL
        )
        """
        self.db.execute_script(sql)
    
    def _create_push_status_table(self):
        """创建推送状态表"""
        table_name = CONFIG.get("database", "last_push_table", fallback="push_status")
        sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            table_name TEXT PRIMARY KEY,
            last_push_time TEXT NOT NULL DEFAULT '2000-01-01 00:00:00'
        )
        """
        self.db.execute_script(sql)
        
        # 插入默认的推送状态记录
        for table in ["sales", "inventory", "accounting"]:
            self.db.execute(
                f"INSERT OR IGNORE INTO {table_name} (table_name, last_push_time) VALUES (?, ?)",
                (table, '2000-01-01 00:00:00')
            )
    
    def _create_sales_goals_table(self):
        """创建销售目标表"""
        sql = """
        CREATE TABLE IF NOT EXISTS sales_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_type TEXT NOT NULL,
            goal_key TEXT NOT NULL,
            target_value REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_script(sql)
        
        # 确保每天/每月都有一个默认目标
        self._ensure_default_goals()
    
    def _migrate_inventory_table(self):
        """迁移库存表（移除stock字段）"""
        # 创建新表
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS inventory_new (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT UNIQUE,
                price REAL DEFAULT 0,
                member_price REAL DEFAULT 0,
                remark TEXT
            )
        """)
        
        # 复制数据
        self.db.execute("""
            INSERT INTO inventory_new (item_id, category, name, price, member_price, remark)
            SELECT item_id, category, name, price, member_price, remark FROM inventory
        """)
        
        # 删除旧表并重命名新表
        self.db.execute("DROP TABLE inventory")
        self.db.execute("ALTER TABLE inventory_new RENAME TO inventory")
    
    def _ensure_default_goals(self):
        """确保默认的销售目标存在"""
        today = date.today()
        day_key = today.strftime("%Y-%m-%d")
        month_key = today.strftime("%Y-%m")
        
        # 检查今日目标是否存在
        if not self.db.exists("sales_goals", "goal_type = ? AND goal_key = ?", ("day", day_key)):
            # 查询最近一次设置的每日目标
            result = self.db.fetch_one(
                "SELECT target_value FROM sales_goals WHERE goal_type='day' ORDER BY created_at DESC LIMIT 1"
            )
            
            if result:
                # 存在历史每日目标，自动继承为今日目标
                self.db.execute(
                    "INSERT INTO sales_goals (goal_type, goal_key, target_value) VALUES (?, ?, ?)",
                    ("day", day_key, result[0])
                )
            else:
                # 首次使用，设置默认目标
                self.db.execute(
                    "INSERT INTO sales_goals (goal_type, goal_key, target_value) VALUES (?, ?, ?)",
                    ("day", day_key, 1000.0)
                )
        
        # 检查当月目标是否存在
        if not self.db.exists("sales_goals", "goal_type = ? AND goal_key = ?", ("month", month_key)):
            self.db.execute(
                "INSERT INTO sales_goals (goal_type, goal_key, target_value) VALUES (?, ?, ?)",
                ("month", month_key, 30000.0)
            )
    
    def _insert_default_data(self):
        """插入默认数据"""
        # 检查用户表是否为空
        user_count = self.db.count("users")
        if user_count == 0:
            # 插入默认用户
            self.db.execute(
                "INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)",
                ("admin", "admin", "profile_photo.png")
            )
        # 注意：已移除所有彩蛋功能
    
    def _handle_upgrades(self):
        """处理数据库升级"""
        # 这里可以添加数据库升级逻辑
        pass


def init_db():
    """初始化数据库（兼容性函数）"""
    initializer = DatabaseInitializer()
    return initializer.initialize()


def get_db_connection():
    """获取数据库连接（兼容性函数）"""
    return db_manager.get_connection()
