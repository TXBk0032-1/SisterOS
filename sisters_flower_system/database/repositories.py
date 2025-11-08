"""
数据访问层 - Repository模式实现
各数据实体的Repository类，提供CRUD操作
"""

from typing import Optional, List, Dict, Any
from .manager import db_manager
from ..models import (
    User, Member, Inventory, Sale, SaleItem, 
    SalesGoal, MemoryReminder, PushStatus,
    ModelConverter
)


class BaseRepository:
    """Repository基类"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = db_manager
    
    def create(self, data: Dict[str, Any]) -> int:
        """创建记录"""
        placeholders = ', '.join(['?' for _ in data])
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            return cursor.lastrowid
    
    def update(self, data: Dict[str, Any], where_clause: str, where_params: tuple = ()) -> int:
        """更新记录"""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"
        
        return self.db.execute(sql, tuple(data.values()) + where_params)
    
    def delete(self, where_clause: str, where_params: tuple = ()) -> int:
        """删除记录"""
        sql = f"DELETE FROM {self.table_name} WHERE {where_clause}"
        return self.db.execute(sql, where_params)
    
    def find_by_id(self, id_value: Any, id_column: str = "id") -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        sql = f"SELECT * FROM {self.table_name} WHERE {id_column} = ?"
        return self.db.fetch_one(sql, (id_value,))
    
    def find_all(self, where_clause: str = "1=1", where_params: tuple = (), 
                 order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """查找所有记录"""
        sql = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit:
            sql += f" LIMIT {limit}"
        
        return self.db.fetch_all(sql, where_params)
    
    def count(self, where_clause: str = "1=1", where_params: tuple = ()) -> int:
        """统计记录数"""
        sql = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
        result = self.db.fetch_one(sql, where_params)
        return result[0] if result else 0
    
    def exists(self, where_clause: str, where_params: tuple = ()) -> bool:
        """检查记录是否存在"""
        return self.count(where_clause, where_params) > 0


class UserRepository(BaseRepository):
    """用户数据访问层"""
    
    def __init__(self):
        super().__init__("users")
    
    def find_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户"""
        data = self.find_by_id(username, "username")
        return ModelConverter.dict_to_user(data) if data else None
    
    def create_user(self, user: User) -> int:
        """创建用户"""
        data = ModelConverter.user_to_dict(user)
        return self.create(data)
    
    def update_user(self, username: str, user: User) -> bool:
        """更新用户"""
        data = ModelConverter.user_to_dict(user)
        return self.update(data, "username = ?", (username,)) > 0
    
    def delete_user(self, username: str) -> bool:
        """删除用户"""
        return self.delete("username = ?", (username,)) > 0
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        data_list = self.find_all()
        return [ModelConverter.dict_to_user(data) for data in data_list]
    
    def authenticate(self, username: str, password: str) -> bool:
        """验证用户登录"""
        sql = "SELECT password FROM users WHERE username = ?"
        result = self.db.fetch_one(sql, (username,))
        return result and result[0] == password


class MemberRepository(BaseRepository):
    """会员数据访问层"""
    
    def __init__(self):
        super().__init__("members")
    
    def find_by_phone(self, phone: str) -> Optional[Member]:
        """根据手机号查找会员"""
        data = self.find_one("phone = ?", (phone,))
        return ModelConverter.dict_to_member(data) if data else None
    
    def create_member(self, member: Member) -> int:
        """创建会员"""
        data = ModelConverter.member_to_dict(member)
        return self.create(data)
    
    def update_member(self, member_id: int, member: Member) -> bool:
        """更新会员"""
        data = ModelConverter.member_to_dict(member)
        return self.update(data, "member_id = ?", (member_id,)) > 0
    
    def update_balance(self, phone: str, balance: float) -> bool:
        """更新会员余额"""
        data = {"balance": balance}
        return self.update(data, "phone = ?", (phone,)) > 0
    
    def get_all_members(self) -> List[Member]:
        """获取所有会员"""
        data_list = self.find_all(order_by="member_id DESC")
        return [ModelConverter.dict_to_member(data) for data in data_list]
    
    def search_members(self, keyword: str) -> List[Member]:
        """搜索会员"""
        where = "phone LIKE ? OR remark LIKE ?"
        params = (f"%{keyword}%", f"%{keyword}%")
        data_list = self.find_all(where, params)
        return [ModelConverter.dict_to_member(data) for data in data_list]


class InventoryRepository(BaseRepository):
    """商品库存数据访问层"""
    
    def __init__(self):
        super().__init__("inventory")
    
    def find_by_name(self, name: str) -> Optional[Inventory]:
        """根据商品名称查找"""
        data = self.find_one("name = ?", (name,))
        return ModelConverter.dict_to_inventory(data) if data else None
    
    def create_item(self, item: Inventory) -> int:
        """创建商品"""
        data = ModelConverter.inventory_to_dict(item)
        return self.create(data)
    
    def update_item(self, item_id: int, item: Inventory) -> bool:
        """更新商品"""
        data = ModelConverter.inventory_to_dict(item)
        return self.update(data, "item_id = ?", (item_id,)) > 0
    
    def get_all_items(self) -> List[Inventory]:
        """获取所有商品"""
        data_list = self.find_all(order_by="item_id DESC")
        return [ModelConverter.dict_to_inventory(data) for data in data_list]
    
    def get_by_category(self, category: str) -> List[Inventory]:
        """根据分类获取商品"""
        data_list = self.find_all("category = ?", (category,))
        return [ModelConverter.dict_to_inventory(data) for data in data_list]
    
    def search_items(self, keyword: str) -> List[Inventory]:
        """搜索商品"""
        where = "name LIKE ? OR category LIKE ? OR remark LIKE ?"
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        data_list = self.find_all(where, params)
        return [ModelConverter.dict_to_inventory(data) for data in data_list]
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        sql = "SELECT DISTINCT category FROM inventory WHERE category IS NOT NULL ORDER BY category"
        results = self.db.fetch_all(sql)
        return [row[0] for row in results if row[0]]


class SaleRepository(BaseRepository):
    """销售数据访问层"""
    
    def __init__(self):
        super().__init__("sales")
    
    def create_sale(self, sale: Sale) -> int:
        """创建销售记录"""
        data = ModelConverter.sale_to_dict(sale)
        return self.create(data)
    
    def get_today_sales(self) -> List[Sale]:
        """获取今日销售记录"""
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        data_list = self.find_all("datetime LIKE ?", (f"{today}%",), "sale_id DESC")
        return [ModelConverter.dict_to_sale(data) for data in data_list]
    
    def get_sales_by_date(self, date_str: str) -> List[Sale]:
        """获取指定日期的销售记录"""
        data_list = self.find_all("datetime LIKE ?", (f"{date_str}%",), "sale_id DESC")
        return [ModelConverter.dict_to_sale(data) for data in data_list]
    
    def get_member_sales(self, phone: str) -> List[Sale]:
        """获取会员销售记录"""
        data_list = self.find_all("member_phone = ?", (phone,), "sale_id DESC")
        return [ModelConverter.dict_to_sale(data) for data in data_list]
    
    def get_daily_sales_total(self, date_str: str = None) -> float:
        """获取指定日期的销售总额"""
        if not date_str:
            from datetime import date
            date_str = date.today().strftime("%Y-%m-%d")
        
        sql = "SELECT SUM(total_paid) FROM sales WHERE datetime LIKE ?"
        result = self.db.fetch_one(sql, (f"{date_str}%",))
        return result[0] if result and result[0] else 0.0
    
    def get_monthly_sales_total(self, month_str: str = None) -> float:
        """获取指定月份的销售总额"""
        if not month_str:
            from datetime import date
            month_str = date.today().strftime("%Y-%m")
        
        sql = "SELECT SUM(total_paid) FROM sales WHERE datetime LIKE ?"
        result = self.db.fetch_one(sql, (f"{month_str}%",))
        return result[0] if result and result[0] else 0.0


class SaleItemRepository(BaseRepository):
    """销售明细数据访问层"""
    
    def __init__(self):
        super().__init__("sale_items")
    
    def create_item(self, item: SaleItem) -> int:
        """创建销售明细"""
        data = ModelConverter.sale_item_to_dict(item)
        return self.create(data)
    
    def get_by_sale_id(self, sale_id: int) -> List[SaleItem]:
        """根据销售ID获取明细"""
        data_list = self.find_all("sale_id = ?", (sale_id,))
        return [ModelConverter.dict_to_sale_item(data) for data in data_list]


class SalesGoalRepository(BaseRepository):
    """销售目标数据访问层"""
    
    def __init__(self):
        super().__init__("sales_goals")
    
    def get_goal(self, period_type: str, target_date: str) -> Optional[SalesGoal]:
        """获取指定周期的销售目标"""
        data = self.find_one("period_type = ? AND target_date = ?", (period_type, target_date))
        return ModelConverter.dict_to_sales_goal(data) if data else None
    
    def set_goal(self, period_type: str, target_date: str, amount: float) -> bool:
        """设置销售目标"""
        # 先尝试更新
        updated = self.update(
            {"target_amount": amount}, 
            "period_type = ? AND target_date = ?", 
            (period_type, target_date)
        )
        
        if updated > 0:
            return True
        
        # 如果没有更新任何记录，则插入新记录
        goal = SalesGoal(period_type=period_type, target_date=target_date, target_amount=amount)
        data = ModelConverter.sales_goal_to_dict(goal)
        return self.create(data) > 0
    
    def get_current_goals(self) -> Dict[str, float]:
        """获取当前周期的销售目标"""
        from datetime import date
        today = date.today()
        day_key = today.strftime("%Y-%m-%d")
        month_key = today.strftime("%Y-%m")
        
        day_goal = self.get_goal("day", day_key)
        month_goal = self.get_goal("month", month_key)
        
        return {
            "day": day_goal.target_amount if day_goal else 0.0,
            "month": month_goal.target_amount if month_goal else 0.0
        }


class MemoryReminderRepository(BaseRepository):
    """内存提醒数据访问层"""
    
    def __init__(self):
        super().__init__("memory_reminder")
    
    def get_settings(self) -> Optional[MemoryReminder]:
        """获取内存提醒设置"""
        data = self.find_one("1=1")  # 获取第一条记录
        return MemoryReminder(
            id=data['id'] if data else None,
            last_reminder_date=data['last_reminder_date'] if data else None,
            reminder_interval=data['reminder_interval'] if data else 0
        ) if data else None
    
    def set_settings(self, interval: int) -> bool:
        """设置内存提醒间隔"""
        now = datetime.now().strftime("%Y-%m-%d")
        
        if self.count() > 0:
            # 更新现有记录
            return self.update(
                {"last_reminder_date": now, "reminder_interval": interval},
                "1=1"
            ) > 0
        else:
            # 创建新记录
            data = {
                "last_reminder_date": now,
                "reminder_interval": interval
            }
            return self.create(data) > 0


class PushStatusRepository(BaseRepository):
    """推送状态数据访问层"""
    
    def __init__(self):
        super().__init__("push_status")
    
    def get_last_push_time(self, table_name: str) -> str:
        """获取表最后推送时间"""
        data = self.find_by_id(table_name, "table_name")
        return data['last_push_time'] if data else "2000-01-01 00:00:00"
    
    def update_push_time(self, table_name: str, push_time: str) -> bool:
        """更新表推送时间"""
        data = {"last_push_time": push_time}
        updated = self.update(data, "table_name = ?", (table_name,))
        
        if updated == 0:
            # 如果没有更新，插入新记录
            data["table_name"] = table_name
            return self.create(data) > 0
        
        return updated > 0
