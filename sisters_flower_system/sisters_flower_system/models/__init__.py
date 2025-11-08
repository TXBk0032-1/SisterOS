"""
数据模型
定义系统中所有的数据模型和实体类
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """用户数据模型"""
    username: str
    password: str
    avatar: Optional[str] = None


@dataclass
class Member:
    """会员数据模型"""
    member_id: Optional[int] = None
    phone: Optional[str] = None
    balance: float = 0.0
    remark: Optional[str] = None
    join_date: Optional[str] = None


@dataclass
class Inventory:
    """商品库存数据模型"""
    item_id: Optional[int] = None
    category: Optional[str] = None
    name: Optional[str] = None
    price: float = 0.0
    member_price: float = 0.0
    remark: Optional[str] = None


@dataclass
class Sale:
    """销售数据模型"""
    sale_id: Optional[int] = None
    datetime: Optional[str] = None
    total_due: float = 0.0
    total_paid: float = 0.0
    is_member: int = 0
    member_phone: Optional[str] = None


@dataclass
class SaleItem:
    """销售明细数据模型"""
    id: Optional[int] = None
    sale_id: Optional[int] = None
    category: Optional[str] = None
    name: Optional[str] = None
    price: float = 0.0
    quantity: int = 0
    remark: Optional[str] = None


@dataclass
class SalesGoal:
    """销售目标数据模型"""
    id: Optional[int] = None
    period_type: str = ""  # "day" 或 "month"
    target_date: str = ""
    target_amount: float = 0.0
    created_at: Optional[str] = None


@dataclass
class MemoryReminder:
    """内存提醒数据模型"""
    id: Optional[int] = None
    last_reminder_date: Optional[str] = None
    reminder_interval: int = 0


@dataclass
class PushStatus:
    """推送状态数据模型"""
    table_name: str
    last_push_time: str = "2000-01-01 00:00:00"


@dataclass
class FestivalInfo:
    """节日信息数据模型"""
    name: str
    greeting: str
    title_suffix: str


class ModelConverter:
    """数据模型转换器"""
    
    @staticmethod
    def dict_to_user(data: dict) -> User:
        """将字典转换为用户模型"""
        return User(
            username=data.get('username', ''),
            password=data.get('password', ''),
            avatar=data.get('avatar')
        )
    
    @staticmethod
    def user_to_dict(user: User) -> dict:
        """将用户模型转换为字典"""
        return {
            'username': user.username,
            'password': user.password,
            'avatar': user.avatar
        }
    
    @staticmethod
    def dict_to_member(data: dict) -> Member:
        """将字典转换为会员模型"""
        return Member(
            member_id=data.get('member_id'),
            phone=data.get('phone'),
            balance=float(data.get('balance', 0.0)),
            remark=data.get('remark'),
            join_date=data.get('join_date')
        )
    
    @staticmethod
    def member_to_dict(member: Member) -> dict:
        """将会员模型转换为字典"""
        return {
            'member_id': member.member_id,
            'phone': member.phone,
            'balance': member.balance,
            'remark': member.remark,
            'join_date': member.join_date
        }
    
    @staticmethod
    def dict_to_inventory(data: dict) -> Inventory:
        """将字典转换为库存模型"""
        return Inventory(
            item_id=data.get('item_id'),
            category=data.get('category'),
            name=data.get('name'),
            price=float(data.get('price', 0.0)),
            member_price=float(data.get('member_price', 0.0)),
            remark=data.get('remark')
        )
    
    @staticmethod
    def inventory_to_dict(inventory: Inventory) -> dict:
        """将库存模型转换为字典"""
        return {
            'item_id': inventory.item_id,
            'category': inventory.category,
            'name': inventory.name,
            'price': inventory.price,
            'member_price': inventory.member_price,
            'remark': inventory.remark
        }
    
    @staticmethod
    def dict_to_sale(data: dict) -> Sale:
        """将字典转换为销售模型"""
        return Sale(
            sale_id=data.get('sale_id'),
            datetime=data.get('datetime'),
            total_due=float(data.get('total_due', 0.0)),
            total_paid=float(data.get('total_paid', 0.0)),
            is_member=int(data.get('is_member', 0)),
            member_phone=data.get('member_phone')
        )
    
    @staticmethod
    def sale_to_dict(sale: Sale) -> dict:
        """将销售模型转换为字典"""
        return {
            'sale_id': sale.sale_id,
            'datetime': sale.datetime,
            'total_due': sale.total_due,
            'total_paid': sale.total_paid,
            'is_member': sale.is_member,
            'member_phone': sale.member_phone
        }
    
    @staticmethod
    def dict_to_sale_item(data: dict) -> SaleItem:
        """将字典转换为销售明细模型"""
        return SaleItem(
            id=data.get('id'),
            sale_id=data.get('sale_id'),
            category=data.get('category'),
            name=data.get('name'),
            price=float(data.get('price', 0.0)),
            quantity=int(data.get('quantity', 0)),
            remark=data.get('remark')
        )
    
    @staticmethod
    def sale_item_to_dict(item: SaleItem) -> dict:
        """将销售明细模型转换为字典"""
        return {
            'id': item.id,
            'sale_id': item.sale_id,
            'category': item.category,
            'name': item.name,
            'price': item.price,
            'quantity': item.quantity,
            'remark': item.remark
        }
    
    @staticmethod
    def dict_to_sales_goal(data: dict) -> SalesGoal:
        """将字典转换为销售目标模型"""
        return SalesGoal(
            id=data.get('id'),
            period_type=data.get('period_type', ''),
            target_date=data.get('target_date', ''),
            target_amount=float(data.get('target_amount', 0.0)),
            created_at=data.get('created_at')
        )
    
    @staticmethod
    def sales_goal_to_dict(goal: SalesGoal) -> dict:
        """将销售目标模型转换为字典"""
        return {
            'id': goal.id,
            'period_type': goal.period_type,
            'target_date': goal.target_date,
            'target_amount': goal.target_amount,
            'created_at': goal.created_at
        }
