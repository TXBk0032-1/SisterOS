"""
库存管理服务
处理商品库存相关的所有业务逻辑
"""

from typing import List, Optional, Dict, Any
from ..database.repositories import InventoryRepository
from ..models import Inventory, ModelConverter


class InventoryService:
    """库存管理服务"""
    
    def __init__(self):
        self.repository = InventoryRepository()
    
    def create_item(self, name: str, category: str = "", price: float = 0.0, 
                   member_price: float = 0.0, remark: str = "") -> bool:
        """创建新商品"""
        try:
            # 检查商品名称是否已存在
            if self.repository.find_by_name(name):
                return False
            
            # 创建商品对象
            item = Inventory(
                name=name,
                category=category,
                price=price,
                member_price=member_price,
                remark=remark
            )
            
            # 保存到数据库
            item_id = self.repository.create_item(item)
            return item_id > 0
            
        except Exception as e:
            print(f"创建商品失败: {e}")
            return False
    
    def get_item_by_name(self, name: str) -> Optional[Inventory]:
        """根据名称获取商品"""
        try:
            return self.repository.find_by_name(name)
        except Exception as e:
            print(f"获取商品失败: {e}")
            return None
    
    def get_all_items(self) -> List[Inventory]:
        """获取所有商品"""
        try:
            return self.repository.get_all_items()
        except Exception as e:
            print(f"获取商品列表失败: {e}")
            return []
    
    def get_items_by_category(self, category: str) -> List[Inventory]:
        """根据分类获取商品"""
        try:
            return self.repository.get_by_category(category)
        except Exception as e:
            print(f"获取分类商品失败: {e}")
            return []
    
    def search_items(self, keyword: str) -> List[Inventory]:
        """搜索商品"""
        try:
            if not keyword.strip():
                return self.get_all_items()
            return self.repository.search_items(keyword.strip())
        except Exception as e:
            print(f"搜索商品失败: {e}")
            return []
    
    def update_item(self, name: str, category: str = None, price: float = None,
                   member_price: float = None, remark: str = None) -> bool:
        """更新商品信息"""
        try:
            item = self.repository.find_by_name(name)
            if not item:
                return False
            
            # 更新字段
            if category is not None:
                item.category = category
            if price is not None:
                item.price = price
            if member_price is not None:
                item.member_price = member_price
            if remark is not None:
                item.remark = remark
            
            return self.repository.update_item(item.item_id, item) > 0
            
        except Exception as e:
            print(f"更新商品失败: {e}")
            return False
    
    def delete_item(self, name: str) -> bool:
        """删除商品"""
        try:
            item = self.repository.find_by_name(name)
            if not item:
                return False
            
            # 检查是否有关联的销售记录
            from ..database.manager import db_manager
            sales_count = db_manager.count(
                "sale_items", "name = ?", (name,)
            )
            
            if sales_count > 0:
                # 有关联记录，不允许删除
                return False
            
            # 删除商品
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item.item_id,))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"删除商品失败: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """获取所有商品分类"""
        try:
            return self.repository.get_categories()
        except Exception as e:
            print(f"获取商品分类失败: {e}")
            return []
    
    def get_inventory_statistics(self) -> Dict[str, Any]:
        """获取库存统计信息"""
        try:
            from ..database.manager import db_manager
            
            # 总商品数
            total_items = db_manager.count("inventory")
            
            # 分类统计
            categories = self.get_categories()
            category_stats = {}
            for category in categories:
                count = db_manager.count("inventory", "category = ?", (category,))
                category_stats[category] = count
            
            # 价格统计
            price_stats = db_manager.fetch_one(
                "SELECT COUNT(*), SUM(price), AVG(price), MIN(price), MAX(price) FROM inventory"
            )
            
            return {
                "total_items": total_items,
                "category_stats": category_stats,
                "price_stats": {
                    "count": price_stats[0] if price_stats else 0,
                    "total": price_stats[1] if price_stats else 0,
                    "average": price_stats[2] if price_stats else 0,
                    "min": price_stats[3] if price_stats else 0,
                    "max": price_stats[4] if price_stats else 0
                }
            }
            
        except Exception as e:
            print(f"获取库存统计失败: {e}")
            return {}
    
    def get_popular_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门商品（按销售数量排序）"""
        try:
            from ..database.manager import db_manager
            
            sql = """
            SELECT si.name, si.category, SUM(si.quantity) as total_quantity,
                   SUM(si.price * si.quantity) as total_sales
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
            GROUP BY si.name, si.category
            ORDER BY total_quantity DESC
            LIMIT ?
            """
            
            results = db_manager.fetch_all(sql, (limit,))
            
            return [
                {
                    "name": row[0],
                    "category": row[1],
                    "total_quantity": row[2],
                    "total_sales": row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"获取热门商品失败: {e}")
            return []
    
    def batch_import_items(self, items_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量导入商品"""
        success_count = 0
        error_count = 0
        duplicate_count = 0
        
        for item_data in items_data:
            try:
                name = item_data.get("name", "").strip()
                category = item_data.get("category", "").strip()
                price = float(item_data.get("price", 0))
                member_price = float(item_data.get("member_price", 0))
                remark = item_data.get("remark", "")
                
                if not name:
                    error_count += 1
                    continue
                
                # 检查是否已存在
                if self.repository.find_by_name(name):
                    duplicate_count += 1
                    continue
                
                # 创建商品
                if self.create_item(name, category, price, member_price, remark):
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"导入商品失败 {item_data}: {e}")
                error_count += 1
        
        return {
            "success": success_count,
            "error": error_count,
            "duplicate": duplicate_count
        }
    
    def export_items(self) -> List[Dict[str, Any]]:
        """导出所有商品数据"""
        try:
            items = self.get_all_items()
            return [
                {
                    "name": item.name,
                    "category": item.category,
                    "price": item.price,
                    "member_price": item.member_price,
                    "remark": item.remark
                }
                for item in items
            ]
        except Exception as e:
            print(f"导出商品数据失败: {e}")
            return []
    
    def get_price_range_items(self, min_price: float = 0, max_price: float = float('inf')) -> List[Inventory]:
        """根据价格范围获取商品"""
        try:
            from ..database.manager import db_manager
            
            sql = """
            SELECT * FROM inventory 
            WHERE price BETWEEN ? AND ?
            ORDER BY price
            """
            
            results = db_manager.fetch_all(sql, (min_price, max_price))
            
            return [ModelConverter.dict_to_inventory(row) for row in results]
            
        except Exception as e:
            print(f"按价格范围获取商品失败: {e}")
            return []
