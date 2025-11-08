#!/usr/bin/env python3
"""
姐妹花销售系统 - 数据库和配置初始化工具
Sisters Flower Sales System - Database and Config Initialization Tool

功能：
1. 数据库结构初始化
2. 配置文件管理
3. 数据迁移和升级
4. 样本数据生成
5. 配置验证
6. 错误恢复

作者: MiniMax Agent
版本: 1.0
"""

import os
import sys
import json
import sqlite3
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import argparse
import tempfile
import subprocess

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self, db_path: Path, config_dir: Path):
        self.db_path = db_path
        self.config_dir = config_dir
        self.logger = self._setup_logging()
        
        # 数据库版本管理
        self.db_version = "4.0"
        self.migration_history = []
        
    def _setup_logging(self):
        """设置日志"""
        log_file = self.config_dir / ".." / "logs" / "database_init.log"
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
    
    def initialize_database(self, create_sample_data: bool = True) -> bool:
        """初始化数据库"""
        self.logger.info("开始数据库初始化...")
        
        try:
            # 创建数据库目录
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 连接到数据库
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 启用外键约束
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # 创建版本表
            self._create_version_table(cursor)
            
            # 执行数据库迁移
            self._execute_migrations(cursor)
            
            # 创建表结构
            self._create_tables(cursor)
            
            # 创建索引
            self._create_indexes(cursor)
            
            # 创建触发器
            self._create_triggers(cursor)
            
            # 插入初始数据
            self._insert_initial_data(cursor)
            
            if create_sample_data:
                self._create_sample_data(cursor)
            
            # 更新版本信息
            self._update_version(cursor)
            
            # 提交事务
            conn.commit()
            conn.close()
            
            self.logger.info("数据库初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            return False
    
    def _create_version_table(self, cursor):
        """创建版本表"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                migration_name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT,
                rollback_sql TEXT
            )
        """)
        self.logger.info("版本表创建完成")
    
    def _create_tables(self, cursor):
        """创建所有数据表"""
        tables = {
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'manager', 'employee')),
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP,
                    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            """,
            
            "categories": """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    parent_id INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES categories (id)
                )
            """,
            
            "products": """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sku TEXT UNIQUE,
                    category_id INTEGER,
                    price REAL NOT NULL,
                    cost_price REAL,
                    stock_quantity INTEGER DEFAULT 0,
                    min_stock_level INTEGER DEFAULT 0,
                    max_stock_level INTEGER DEFAULT 0,
                    unit TEXT DEFAULT '个',
                    description TEXT,
                    barcode TEXT,
                    image_path TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """,
            
            "suppliers": """
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    tax_number TEXT,
                    payment_terms TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            "customers": """
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    tax_number TEXT,
                    customer_type TEXT DEFAULT 'regular' CHECK (customer_type IN ('regular', 'vip', 'wholesale')),
                    credit_limit REAL DEFAULT 0,
                    current_balance REAL DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_purchase_date TIMESTAMP
                )
            """,
            
            "sales": """
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_number TEXT UNIQUE NOT NULL,
                    customer_id INTEGER,
                    user_id INTEGER,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    subtotal REAL NOT NULL,
                    tax_amount REAL DEFAULT 0,
                    discount_amount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    payment_method TEXT DEFAULT 'cash' CHECK (payment_method IN ('cash', 'card', 'transfer', 'mixed')),
                    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'partial', 'refunded')),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """,
            
            "sale_items": """
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity REAL NOT NULL,
                    unit_price REAL NOT NULL,
                    discount_rate REAL DEFAULT 0,
                    total_price REAL NOT NULL,
                    cost_price REAL,
                    profit_margin REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """,
            
            "purchases": """
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_number TEXT UNIQUE NOT NULL,
                    supplier_id INTEGER,
                    user_id INTEGER,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expected_date DATE,
                    subtotal REAL NOT NULL,
                    tax_amount REAL DEFAULT 0,
                    discount_amount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'partial')),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """,
            
            "purchase_items": """
                CREATE TABLE IF NOT EXISTS purchase_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity REAL NOT NULL,
                    unit_cost REAL NOT NULL,
                    total_cost REAL NOT NULL,
                    received_quantity REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (purchase_id) REFERENCES purchases (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """,
            
            "inventory_movements": """
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL CHECK (movement_type IN ('in', 'out', 'adjustment', 'transfer')),
                    quantity REAL NOT NULL,
                    reference_type TEXT CHECK (reference_type IN ('purchase', 'sale', 'adjustment', 'transfer')),
                    reference_id INTEGER,
                    unit_cost REAL,
                    total_cost REAL,
                    reason TEXT,
                    notes TEXT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """,
            
            "settings": """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    data_type TEXT DEFAULT 'string' CHECK (data_type IN ('string', 'number', 'boolean', 'json')),
                    category TEXT DEFAULT 'general',
                    description TEXT,
                    is_encrypted BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by INTEGER,
                    FOREIGN KEY (updated_by) REFERENCES users (id)
                )
            """,
            
            "audit_log": """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    table_name TEXT,
                    record_id INTEGER,
                    old_values TEXT,
                    new_values TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """,
            
            "notifications": """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT DEFAULT 'info' CHECK (type IN ('info', 'warning', 'error', 'success')),
                    is_read BOOLEAN DEFAULT FALSE,
                    action_url TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
        }
        
        for table_name, create_sql in tables.items():
            cursor.execute(create_sql)
            self.logger.info(f"表 '{table_name}' 创建完成")
    
    def _create_indexes(self, cursor):
        """创建数据库索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)",
            "CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)",
            "CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_movements_product ON inventory_movements(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_movements_date ON inventory_movements(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_date ON audit_log(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(is_read, user_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.logger.info("数据库索引创建完成")
    
    def _create_triggers(self, cursor):
        """创建数据库触发器"""
        triggers = [
            # 更新产品库存
            """
            CREATE TRIGGER IF NOT EXISTS update_product_stock
            AFTER INSERT ON sale_items
            FOR EACH ROW
            BEGIN
                UPDATE products 
                SET stock_quantity = stock_quantity - NEW.quantity,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.product_id;
            END
            """,
            
            # 创建库存记录
            """
            CREATE TRIGGER IF NOT EXISTS create_inventory_movement_sale
            AFTER INSERT ON sale_items
            FOR EACH ROW
            BEGIN
                INSERT INTO inventory_movements 
                (product_id, movement_type, quantity, reference_type, reference_id, unit_cost, total_cost, reason)
                VALUES (NEW.product_id, 'out', NEW.quantity, 'sale', NEW.sale_id, NEW.cost_price, NEW.quantity * NEW.cost_price, '销售出库');
            END
            """,
            
            # 更新客户最后购买日期
            """
            CREATE TRIGGER IF NOT EXISTS update_customer_last_purchase
            AFTER INSERT ON sales
            FOR EACH ROW
            WHEN NEW.customer_id IS NOT NULL
            BEGIN
                UPDATE customers 
                SET last_purchase_date = NEW.sale_date
                WHERE id = NEW.customer_id;
            END
            """,
            
            # 自动更新updated_at字段
            """
            CREATE TRIGGER IF NOT EXISTS update_products_updated_at
            AFTER UPDATE ON products
            FOR EACH ROW
            BEGIN
                UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
            """
        ]
        
        for trigger_sql in triggers:
            cursor.execute(trigger_sql)
        
        self.logger.info("数据库触发器创建完成")
    
    def _insert_initial_data(self, cursor):
        """插入初始数据"""
        # 系统设置
        settings = [
            ('app_name', '姐妹花销售系统', 'string', 'system', '应用程序名称'),
            ('app_version', self.db_version, 'string', 'system', '应用程序版本'),
            ('company_name', '姐妹花公司', 'string', 'company', '公司名称'),
            ('company_address', '', 'string', 'company', '公司地址'),
            ('company_phone', '', 'string', 'company', '公司电话'),
            ('company_email', '', 'string', 'company', '公司邮箱'),
            ('default_currency', 'CNY', 'string', 'system', '默认货币'),
            ('tax_rate', '0.13', 'number', 'system', '默认税率'),
            ('low_stock_alert', '10', 'number', 'inventory', '低库存预警阈值'),
            ('auto_backup', 'true', 'boolean', 'system', '自动备份'),
            ('backup_interval_hours', '24', 'number', 'system', '备份间隔（小时）'),
            ('session_timeout_minutes', '60', 'number', 'security', '会话超时（分钟）'),
            ('max_login_attempts', '3', 'number', 'security', '最大登录尝试次数'),
            ('theme', 'light', 'string', 'ui', '界面主题'),
            ('language', 'zh-CN', 'string', 'ui', '界面语言')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO settings (key, value, data_type, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, settings)
        
        # 默认分类
        categories = [
            ('花卉', '各种花卉产品'),
            ('盆栽', '盆栽植物'),
            ('花束', '精美花束'),
            ('花盒', '礼盒包装'),
            ('装饰品', '装饰用品'),
            ('工具', '园艺工具')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO categories (name, description)
            VALUES (?, ?)
        """, categories)
        
        self.logger.info("初始数据插入完成")
    
    def _create_sample_data(self, cursor):
        """创建样本数据"""
        # 默认管理员用户
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, 'admin', '系统管理员', 'admin@sisters.com')
        """, ('admin', admin_password))
        
        # 样本客户
        customers = [
            ('张三', '张三', '13800138001', 'zhangsan@email.com', '北京市朝阳区xxx街道', 'regular', 0, 0),
            ('李四', '李四', '13800138002', 'lisi@email.com', '上海市浦东新区xxx路', 'vip', 5000, 0),
            ('王五', '王五', '13800138003', 'wangwu@email.com', '广州市天河区xxx大道', 'wholesale', 20000, 0)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO customers (name, contact_person, phone, email, address, customer_type, credit_limit, current_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, customers)
        
        # 样本供应商
        suppliers = [
            ('花卉批发市场', '赵经理', '13900139001', 'market@flower.com', '花卉批发市场A区', '30天'),
            ('园艺用品公司', '钱经理', '13900139002', 'garden@supplier.com', '园艺用品公司B区', '15天')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO suppliers (name, contact_person, phone, email, address, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        """, suppliers)
        
        # 样本产品
        products = [
            ('红玫瑰', 'R001', 1, 15.00, 8.00, 100, 10, 500, '枝', '经典红玫瑰', '', '', '红玫瑰图片.jpg'),
            ('白玫瑰', 'R002', 1, 18.00, 10.00, 80, 10, 300, '枝', '纯洁白玫瑰', '', '', '白玫瑰图片.jpg'),
            ('康乃馨', 'C001', 1, 8.00, 4.00, 200, 20, 1000, '枝', '温馨康乃馨', '', '', '康乃馨图片.jpg'),
            ('百合花', 'L001', 1, 25.00, 15.00, 60, 5, 200, '枝', '清香百合', '', '', '百合图片.jpg'),
            ('盆栽绿萝', 'P001', 2, 35.00, 20.00, 50, 5, 150, '盆', '室内绿植', '', '', '绿萝图片.jpg'),
            ('精美花束A', 'B001', 3, 88.00, 50.00, 20, 2, 50, '束', '精美花束组合', '', '', '花束A图片.jpg')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO products (name, sku, category_id, price, cost_price, stock_quantity, min_stock_level, max_stock_level, unit, description, barcode, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, products)
        
        self.logger.info("样本数据创建完成")
    
    def _update_version(self, cursor):
        """更新版本信息"""
        cursor.execute("""
            INSERT INTO db_version (version, migration_name, checksum)
            VALUES (?, ?, ?)
        """, (self.db_version, f"init_v{self.db_version}", "init"))
    
    def _execute_migrations(self, cursor):
        """执行数据库迁移"""
        # 这里可以添加从旧版本到新版本的迁移逻辑
        pass
    
    def backup_database(self, backup_path: Path) -> bool:
        """备份数据库"""
        try:
            if not self.db_path.exists():
                self.logger.error("数据库文件不存在")
                return False
            
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建数据库备份
            conn = sqlite3.connect(str(self.db_path))
            backup_conn = sqlite3.connect(str(backup_path))
            conn.backup(backup_conn)
            backup_conn.close()
            conn.close()
            
            # 备份元数据
            metadata = {
                "backup_time": datetime.now().isoformat(),
                "source_db": str(self.db_path),
                "backup_db": str(backup_path),
                "db_version": self.db_version,
                "file_size": self.db_path.stat().st_size
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"数据库备份完成: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库备份失败: {e}")
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """恢复数据库"""
        try:
            if not backup_path.exists():
                self.logger.error("备份文件不存在")
                return False
            
            # 创建当前数据库的备份
            if self.db_path.exists():
                backup_current = self.db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                shutil.copy2(self.db_path, backup_current)
                self.logger.info(f"当前数据库已备份到: {backup_current}")
            
            # 恢复数据库
            conn = sqlite3.connect(str(backup_path))
            restore_conn = sqlite3.connect(str(self.db_path))
            conn.backup(restore_conn)
            restore_conn.close()
            conn.close()
            
            self.logger.info(f"数据库恢复完成: {self.db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库恢复失败: {e}")
            return False

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_file = config_dir / "app_config.json"
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """设置日志"""
        log_file = self.config_dir / ".." / "logs" / "config_manager.log"
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
    
    def create_default_config(self) -> bool:
        """创建默认配置"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            default_config = {
                "app": {
                    "name": "姐妹花销售系统",
                    "version": "4.0",
                    "author": "MiniMax Agent",
                    "description": "现代化销售管理系统",
                    "build_date": datetime.now().isoformat()
                },
                "database": {
                    "type": "sqlite",
                    "connection_timeout": 30,
                    "backup_enabled": True,
                    "backup_interval_hours": 24,
                    "backup_retention_days": 30,
                    "auto_vacuum": True,
                    "wal_mode": True
                },
                "ui": {
                    "theme": "light",
                    "accent_color": "#0078d4",
                    "font_family": "Microsoft YaHei UI",
                    "font_size": 10,
                    "window_size": "1200x800",
                    "min_window_size": "800x600",
                    "max_window_size": "1920x1080",
                    "auto_save_window_size": True,
                    "show_splash_screen": True
                },
                "security": {
                    "session_timeout_minutes": 60,
                    "max_login_attempts": 3,
                    "password_min_length": 6,
                    "require_strong_password": False,
                    "password_expiry_days": 0,
                    "enable_audit_log": True,
                    "encrypt_sensitive_data": False
                },
                "features": {
                    "enable_barcode": True,
                    "enable_inventory_tracking": True,
                    "enable_customer_management": True,
                    "enable_supplier_management": True,
                    "enable_reporting": True,
                    "enable_multi_user": True,
                    "enable_api": False
                },
                "notifications": {
                    "enable_low_stock_alerts": True,
                    "enable_backup_reminders": True,
                    "enable_system_notifications": True,
                    "notification_sound": True
                },
                "backup": {
                    "auto_backup": True,
                    "backup_interval_hours": 24,
                    "backup_retention_days": 30,
                    "backup_compression": True,
                    "backup_location": str(self.config_dir.parent / "backup")
                },
                "logging": {
                    "level": "INFO",
                    "file": str(self.config_dir.parent / "logs" / "system.log"),
                    "max_file_size_mb": 10,
                    "backup_count": 5,
                    "console_output": True
                },
                "performance": {
                    "max_recent_files": 10,
                    "cache_size_mb": 100,
                    "enable_caching": True,
                    "lazy_loading": True
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"默认配置创建完成: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建默认配置失败: {e}")
            return False
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """加载配置"""
        try:
            if not self.config_file.exists():
                self.logger.warning("配置文件不存在，创建默认配置")
                self.create_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info("配置加载成功")
            return config
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return None
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 创建备份
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                shutil.copy2(self.config_file, backup_file)
            
            # 保存新配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info("配置保存成功")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证必需的配置项
        required_sections = ['app', 'database', 'ui', 'security']
        for section in required_sections:
            if section not in config:
                errors.append(f"缺少必需的配置节: {section}")
        
        # 验证数据库配置
        if 'database' in config:
            db_config = config['database']
            if 'type' not in db_config or db_config['type'] not in ['sqlite', 'mysql', 'postgresql']:
                errors.append("数据库类型配置无效")
            
            if 'backup_enabled' in db_config and not isinstance(db_config['backup_enabled'], bool):
                errors.append("备份启用配置必须是布尔值")
        
        # 验证UI配置
        if 'ui' in config:
            ui_config = config['ui']
            if 'theme' in ui_config and ui_config['theme'] not in ['light', 'dark', 'auto']:
                errors.append("界面主题配置无效")
        
        # 验证安全配置
        if 'security' in config:
            sec_config = config['security']
            if 'session_timeout_minutes' in sec_config:
                try:
                    timeout = int(sec_config['session_timeout_minutes'])
                    if timeout < 1 or timeout > 1440:
                        errors.append("会话超时时间必须在1-1440分钟之间")
                except (ValueError, TypeError):
                    errors.append("会话超时时间必须是数字")
        
        self.logger.info(f"配置验证完成，发现 {len(errors)} 个问题")
        return errors

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库和配置管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 初始化数据库命令
    init_db_parser = subparsers.add_parser('init-db', help='初始化数据库')
    init_db_parser.add_argument('--db-path', type=Path, required=True, help='数据库文件路径')
    init_db_parser.add_argument('--config-dir', type=Path, required=True, help='配置目录路径')
    init_db_parser.add_argument('--no-sample-data', action='store_true', help='不创建样本数据')
    
    # 备份数据库命令
    backup_parser = subparsers.add_parser('backup-db', help='备份数据库')
    backup_parser.add_argument('--db-path', type=Path, required=True, help='数据库文件路径')
    backup_parser.add_argument('--backup-path', type=Path, required=True, help='备份文件路径')
    
    # 恢复数据库命令
    restore_parser = subparsers.add_parser('restore-db', help='恢复数据库')
    restore_parser.add_argument('--db-path', type=Path, required=True, help='目标数据库文件路径')
    restore_parser.add_argument('--backup-path', type=Path, required=True, help='备份文件路径')
    
    # 配置管理命令
    init_config_parser = subparsers.add_parser('init-config', help='初始化配置')
    init_config_parser.add_argument('--config-dir', type=Path, required=True, help='配置目录路径')
    
    validate_config_parser = subparsers.add_parser('validate-config', help='验证配置')
    validate_config_parser.add_argument('--config-file', type=Path, required=True, help='配置文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'init-db':
            initializer = DatabaseInitializer(args.db_path, args.config_dir)
            success = initializer.initialize_database(not args.no_sample_data)
            sys.exit(0 if success else 1)
        
        elif args.command == 'backup-db':
            initializer = DatabaseInitializer(args.db_path, args.config_dir)
            success = initializer.backup_database(args.backup_path)
            sys.exit(0 if success else 1)
        
        elif args.command == 'restore-db':
            initializer = DatabaseInitializer(args.db_path, args.config_dir)
            success = initializer.restore_database(args.backup_path)
            sys.exit(0 if success else 1)
        
        elif args.command == 'init-config':
            config_manager = ConfigManager(args.config_dir)
            success = config_manager.create_default_config()
            sys.exit(0 if success else 1)
        
        elif args.command == 'validate-config':
            config_manager = ConfigManager(args.config_file.parent)
            config = config_manager.load_config()
            if config:
                errors = config_manager.validate_config(config)
                if errors:
                    print("配置验证失败:")
                    for error in errors:
                        print(f"  - {error}")
                    sys.exit(1)
                else:
                    print("配置验证通过")
                    sys.exit(0)
            else:
                print("配置加载失败")
                sys.exit(1)
    
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()