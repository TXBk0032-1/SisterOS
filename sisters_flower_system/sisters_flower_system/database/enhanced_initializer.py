#!/usr/bin/env python3
"""
增强版数据库初始化脚本
初始化数据库表结构并添加示例数据
"""

import os
import random
import sqlite3
from datetime import datetime, date, timedelta


class EnhancedDatabaseInitializer:
    """增强版数据库初始化器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def initialize_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 创建所有表
            self.create_all_tables(cursor)
            
            # 创建索引
            self.create_indexes(cursor)
            
            # 插入示例数据
            self.insert_sample_data(cursor)
            
            conn.commit()
            print("✅ 数据库初始化成功")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 数据库初始化失败: {e}")
            raise
        finally:
            conn.close()
    
    def create_all_tables(self, cursor):
        """创建所有数据表"""
        
        # 产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                cost REAL DEFAULT 0,
                stock INTEGER DEFAULT 0,
                alert_threshold INTEGER DEFAULT 10,
                barcode TEXT UNIQUE,
                description TEXT,
                image_path TEXT,
                supplier TEXT,
                unit TEXT DEFAULT '个',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 会员表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                email TEXT,
                birthday DATE,
                balance REAL DEFAULT 0,
                points INTEGER DEFAULT 0,
                level TEXT DEFAULT '普通',
                address TEXT,
                note TEXT,
                gender TEXT DEFAULT '未知',
                occupation TEXT,
                registration_date DATE DEFAULT CURRENT_DATE,
                last_visit_date DATE,
                total_consumption REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 销售表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                member_id INTEGER,
                total_amount REAL NOT NULL,
                discount REAL DEFAULT 0,
                final_amount REAL NOT NULL,
                payment_method TEXT,
                payment_status TEXT DEFAULT '已完成',
                cashier TEXT DEFAULT '系统',
                notes TEXT,
                receipt_number TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # 销售明细表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # 库存变动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                change_type TEXT NOT NULL,
                quantity_change INTEGER NOT NULL,
                previous_stock INTEGER,
                new_stock INTEGER,
                reason TEXT,
                operator TEXT DEFAULT '系统',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # 目标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                target_value REAL NOT NULL,
                current_value REAL DEFAULT 0,
                unit TEXT DEFAULT '',
                deadline DATE NOT NULL,
                status TEXT DEFAULT '进行中',
                priority TEXT DEFAULT '普通',
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        ''')
        
        # 系统设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT UNIQUE NOT NULL,
                key_value TEXT,
                description TEXT,
                data_type TEXT DEFAULT 'string',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 消费记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                description TEXT,
                operator TEXT DEFAULT '系统',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        print("✅ 数据表创建完成")
    
    def create_indexes(self, cursor):
        """创建数据库索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)",
            "CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone)",
            "CREATE INDEX IF NOT EXISTS idx_members_name ON members(name)",
            "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)",
            "CREATE INDEX IF NOT EXISTS idx_sales_member ON sales(member_id)",
            "CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)",
            "CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_logs_product ON inventory_logs(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_goals_type ON goals(type)",
            "CREATE INDEX IF NOT EXISTS idx_goals_deadline ON goals(deadline)",
            "CREATE INDEX IF NOT EXISTS idx_member_transactions_member ON member_transactions(member_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ 索引创建完成")
    
    def insert_sample_data(self, cursor):
        """插入示例数据"""
        
        # 插入示例产品
        sample_products = [
            ("红玫瑰", "鲜花", 15.00, 8.00, 50, 5, "R001", "优质红玫瑰", None, "花卉批发市场", "支", "2024-01-01"),
            ("白玫瑰", "鲜花", 18.00, 10.00, 30, 5, "R002", "纯洁白玫瑰", None, "花卉批发市场", "支", "2024-01-01"),
            ("康乃馨", "鲜花", 8.00, 4.50, 100, 10, "K001", "温馨康乃馨", None, "花卉批发市场", "支", "2024-01-01"),
            ("百合花", "鲜花", 25.00, 15.00, 20, 3, "B001", "香水百合", None, "花卉批发市场", "支", "2024-01-01"),
            ("向日葵", "鲜花", 12.00, 6.00, 40, 5, "S001", "阳光向日葵", None, "花卉批发市场", "支", "2024-01-01"),
            ("满天星", "配花", 10.00, 5.00, 60, 8, "M001", "浪漫满天星", None, "花卉批发市场", "支", "2024-01-01"),
            ("紫罗兰", "鲜花", 16.00, 9.00, 25, 3, "V001", "优雅紫罗兰", None, "花卉批发市场", "支", "2024-01-01"),
            ("勿忘我", "配花", 8.00, 4.00, 80, 10, "F001", "勿忘我配花", None, "花卉批发市场", "支", "2024-01-01"),
            ("玫瑰花束", "花束", 88.00, 45.00, 15, 2, "FB001", "精美玫瑰花束", None, "花艺设计", "束", "2024-01-01"),
            ("婚庆花束", "花束", 188.00, 95.00, 8, 1, "HB001", "婚庆专用花束", None, "花艺设计", "束", "2024-01-01")
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, price, cost, stock, alert_threshold, barcode, 
                                description, image_path, supplier, unit, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [(p + (datetime.now(), datetime.now())) for p in sample_products])
        
        # 插入示例会员
        sample_members = [
            ("张三", "13800138001", "zhangsan@email.com", "1990-05-15", 150.50, 280, "银卡", "北京市朝阳区", "老客户", "男", "工程师", date.today() - timedelta(days=30), date.today(), 1500.00),
            ("李四", "13800138002", "lisi@email.com", "1985-08-22", 89.30, 156, "金卡", "上海市浦东新区", "VIP客户", "女", "医生", date.today() - timedelta(days=25), date.today() - timedelta(days=1), 2200.00),
            ("王五", "13800138003", "wangwu@email.com", "1992-12-03", 0.00, 45, "普通", "广州市天河区", None, "男", "教师", date.today() - timedelta(days=20), date.today() - timedelta(days=3), 680.00),
            ("赵六", "13800138004", "zhaoliu@email.com", "1988-03-18", 320.80, 456, "金卡", "深圳市南山区", "大客户", "女", "商人", date.today() - timedelta(days=18), date.today(), 3200.00),
            ("钱七", "13800138005", "qianqi@email.com", "1995-07-10", 12.00, 23, "普通", "杭州市西湖区", None, "女", "学生", date.today() - timedelta(days=15), date.today() - timedelta(days=5), 180.00)
        ]
        
        cursor.executemany('''
            INSERT INTO members (name, phone, email, birthday, balance, points, level, address, 
                               note, gender, occupation, registration_date, last_visit_date, 
                               total_consumption, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [(m + (datetime.now(), datetime.now())) for m in sample_members])
        
        # 插入示例销售记录
        sample_sales = []
        for i in range(20):
            sale_date = datetime.now() - timedelta(days=random.randint(0, 30))
            member_id = random.choice([1, 2, 3, 4, 5, None])  # 包含散客
            total_amount = round(random.uniform(20, 200), 2)
            discount = round(total_amount * random.uniform(0, 0.1), 2)
            final_amount = total_amount - discount
            
            sample_sales.append((
                sale_date,
                member_id,
                total_amount,
                discount,
                final_amount,
                random.choice(["现金", "微信", "支付宝", "银行卡"]),
                "已完成",
                "系统",
                f"销售备注 {i+1}",
                f"R{1000+i:04d}",
                datetime.now(),
                datetime.now()
            ))
        
        cursor.executemany('''
            INSERT INTO sales (sale_date, member_id, total_amount, discount, final_amount, 
                             payment_method, payment_status, cashier, notes, receipt_number, 
                             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_sales)
        
        # 插入示例销售明细
        cursor.execute("SELECT id FROM sales")
        sales = cursor.fetchall()
        
        cursor.execute("SELECT id, price FROM products")
        products = cursor.fetchall()
        
        sample_sale_items = []
        for sale_id, in sales:
            # 每个销售包含1-3个商品
            num_items = random.randint(1, 3)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product_id, product_price in selected_products:
                quantity = random.randint(1, 3)
                total_price = product_price * quantity
                discount = round(total_price * random.uniform(0, 0.1), 2)
                
                sample_sale_items.append((
                    sale_id,
                    product_id,
                    quantity,
                    product_price,
                    total_price,
                    discount,
                    datetime.now()
                ))
        
        cursor.executemany('''
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price, discount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_sale_items)
        
        # 插入示例目标
        sample_goals = [
            ("月度销售额目标", "销售", 50000.00, 15680.50, "元", date.today() + timedelta(days=15), "进行中", "高", "本月销售目标"),
            ("会员增长目标", "会员", 100.00, 67.00, "人", date.today() + timedelta(days=30), "进行中", "普通", "新增会员数量目标"),
            ("利润率目标", "利润", 30.0, 24.5, "%", date.today() + timedelta(days=60), "进行中", "普通", "毛利率目标"),
            ("库存周转率", "库存", 5.0, 3.2, "次/月", date.today() + timedelta(days=45), "进行中", "低", "月度库存周转次数")
        ]
        
        cursor.executemany('''
            INSERT INTO goals (name, type, target_value, current_value, unit, deadline, status, priority, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [(g + (datetime.now(), datetime.now())) for g in sample_goals])
        
        # 插入系统设置
        system_settings = [
            ("shop_name", "姐妹花花店", "店铺名称", "string"),
            ("shop_address", "北京市朝阳区花卉市场", "店铺地址", "string"),
            ("shop_phone", "010-12345678", "店铺电话", "string"),
            ("tax_rate", "0.13", "税率", "float"),
            ("currency", "CNY", "货币单位", "string"),
            ("auto_backup", "true", "自动备份", "boolean"),
            ("backup_interval", "24", "备份间隔(小时)", "integer"),
            ("low_stock_alert", "true", "低库存预警", "boolean"),
            ("member_birthday_alert", "true", "会员生日提醒", "boolean")
        ]
        
        cursor.executemany('''
            INSERT INTO system_settings (key_name, key_value, description, data_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [(s + (datetime.now(), datetime.now())) for s in system_settings])
        
        print("✅ 示例数据插入完成")
    
    def backup_database(self, backup_path: str = None):
        """备份数据库"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"sisters_flowers_enhanced_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ 数据库备份成功: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            return None


def main():
    """主函数"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sisters_flowers_enhanced.db')
    
    # 创建初始化器
    initializer = EnhancedDatabaseInitializer(db_path)
    
    try:
        # 初始化数据库
        initializer.initialize_database()
        
        # 创建备份
        backup_path = initializer.backup_database()
        
        print("\n🎉 增强版数据库初始化完成！")
        print(f"📁 数据库文件: {db_path}")
        if backup_path:
            print(f"💾 备份文件: {backup_path}")
        
        # 显示统计信息
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 统计表记录数
        tables = ['products', 'members', 'sales', 'goals', 'system_settings']
        print("\n📊 数据库统计:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")


if __name__ == "__main__":
    main()
