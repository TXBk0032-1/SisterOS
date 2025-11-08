"""
销售管理服务
处理销售相关的所有业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..database.repositories import SalesRepository, SaleItemRepository, MemberRepository
from ..models import Sale, SaleItem
from ..services.member_service import MemberService


class SalesService:
    """销售管理服务"""
    
    def __init__(self):
        self.sales_repo = SalesRepository()
        self.sale_items_repo = SaleItemRepository()
        self.member_service = MemberService()
    
    def create_sale(self, items: List[Dict], is_member: bool = False, 
                   member_phone: str = "", total_due: float = 0, 
                   total_paid: float = 0) -> Optional[int]:
        """创建销售记录"""
        try:
            # 创建销售主记录
            sale = Sale(
                datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_due=total_due,
                total_paid=total_paid,
                is_member=1 if is_member else 0,
                member_phone=member_phone if is_member else None
            )
            
            sale_id = self.sales_repo.create_sale(sale)
            if not sale_id:
                return None
            
            # 创建销售明细
            for item_data in items:
                sale_item = SaleItem(
                    sale_id=sale_id,
                    category=item_data.get('category', ''),
                    name=item_data.get('name', ''),
                    price=item_data.get('price', 0),
                    quantity=item_data.get('quantity', 0),
                    remark=item_data.get('remark', '')
                )
                self.sale_items_repo.create_item(sale_item)
            
            # 如果是会员，更新会员余额
            if is_member and member_phone:
                self.member_service.deduct_balance(member_phone, total_paid)
            
            return sale_id
            
        except Exception as e:
            print(f"创建销售记录失败: {e}")
            return None
    
    def get_today_sales(self) -> List[Sale]:
        """获取今日销售记录"""
        return self.sales_repo.get_today_sales()
    
    def get_sales_statistics(self, date_str: str = None) -> Dict[str, Any]:
        """获取销售统计"""
        if not date_str:
            date_str = date.today().strftime("%Y-%m-%d")
        
        # 销售额统计
        total_sales = self.sales_repo.get_daily_sales_total(date_str)
        
        # 会员销售额
        from ..database.manager import db_manager
        member_sales = db_manager.fetch_one(
            "SELECT SUM(total_paid) FROM sales WHERE datetime LIKE ? AND is_member = 1",
            (f"{date_str}%",)
        )
        member_sales_total = member_sales[0] if member_sales and member_sales[0] else 0
        
        # 销售笔数
        sales_count = db_manager.count("sales", "datetime LIKE ?", (f"{date_str}%",))
        
        # 平均客单价
        avg_amount = total_sales / sales_count if sales_count > 0 else 0
        
        return {
            "total_sales": total_sales,
            "member_sales": member_sales_total,
            "cash_sales": total_sales - member_sales_total,
            "sales_count": sales_count,
            "avg_amount": avg_amount
        }
    
    def get_sales_by_period(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取指定时间段内的销售数据"""
        try:
            from datetime import date as date_module
            from ..database.manager import db_manager
            
            sql = """
            SELECT datetime, SUM(total_paid) as daily_sales, COUNT(*) as sales_count
            FROM sales 
            WHERE datetime BETWEEN ? AND ?
            GROUP BY date(datetime)
            ORDER BY datetime
            """
            
            results = db_manager.fetch_all(sql, (start_date, end_date))
            
            return [
                {
                    "date": row[0][:10],  # 只取日期部分
                    "daily_sales": row[1],
                    "sales_count": row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"获取时间段销售数据失败: {e}")
            return []
    
    def get_top_selling_items(self, limit: int = 10, date_str: str = None) -> List[Dict[str, Any]]:
        """获取热销商品排行"""
        try:
            from datetime import date as date_module
            if not date_str:
                date_str = date_module.today().strftime("%Y-%m-%d")
            
            from ..database.manager import db_manager
            
            sql = """
            SELECT si.name, si.category, SUM(si.quantity) as total_quantity,
                   SUM(si.price * si.quantity) as total_revenue
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.datetime LIKE ?
            GROUP BY si.name, si.category
            ORDER BY total_quantity DESC
            LIMIT ?
            """
            
            results = db_manager.fetch_all(sql, (f"{date_str}%", limit))
            
            return [
                {
                    "name": row[0],
                    "category": row[1],
                    "total_quantity": row[2],
                    "total_revenue": row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"获取热销商品失败: {e}")
            return []
    
    def refund_sale(self, sale_id: int) -> bool:
        """处理退款"""
        try:
            from ..database.manager import db_manager
            
            conn = db_manager.get_connection()
            cur = conn.cursor()
            
            # 获取销售记录
            cur.execute("SELECT is_member, member_phone, total_paid FROM sales WHERE sale_id = ?", (sale_id,))
            sale = cur.fetchone()
            
            if not sale:
                conn.close()
                return False
            
            is_member, member_phone, total_paid = sale
            
            # 如果是会员，退款到会员余额
            if is_member and member_phone:
                self.member_service.add_balance(member_phone, total_paid)
            
            # 标记为已退款（这里简单地删除记录）
            cur.execute("DELETE FROM sale_items WHERE sale_id = ?", (sale_id,))
            cur.execute("DELETE FROM sales WHERE sale_id = ?", (sale_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"退款处理失败: {e}")
            return False
