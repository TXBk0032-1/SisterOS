"""
会员管理服务
处理会员相关的所有业务逻辑
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..database.repositories import MemberRepository
from ..models import Member, ModelConverter
from ..config.settings import DB_PATH
import sqlite3


class MemberService:
    """会员管理服务"""
    
    def __init__(self):
        self.repository = MemberRepository()
        self.db_path = DB_PATH
    
    def create_member(self, phone: str, remark: str = "", initial_balance: float = 0.0) -> bool:
        """创建新会员"""
        try:
            # 检查手机号是否已存在
            if self.repository.find_by_phone(phone):
                return False
            
            # 创建会员对象
            member = Member(
                phone=phone,
                balance=initial_balance,
                remark=remark,
                join_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # 保存到数据库
            member_id = self.repository.create_member(member)
            return member_id > 0
            
        except Exception as e:
            print(f"创建会员失败: {e}")
            return False
    
    def get_member_by_phone(self, phone: str) -> Optional[Member]:
        """根据手机号获取会员"""
        try:
            return self.repository.find_by_phone(phone)
        except Exception as e:
            print(f"获取会员失败: {e}")
            return None
    
    def get_all_members(self) -> List[Member]:
        """获取所有会员"""
        try:
            return self.repository.get_all_members()
        except Exception as e:
            print(f"获取会员列表失败: {e}")
            return []
    
    def search_members(self, keyword: str) -> List[Member]:
        """搜索会员"""
        try:
            if not keyword.strip():
                return self.get_all_members()
            return self.repository.search_members(keyword.strip())
        except Exception as e:
            print(f"搜索会员失败: {e}")
            return []
    
    def update_member(self, phone: str, remark: str = None, balance: float = None) -> bool:
        """更新会员信息"""
        try:
            member = self.repository.find_by_phone(phone)
            if not member:
                return False
            
            # 更新字段
            if remark is not None:
                member.remark = remark
            if balance is not None:
                member.balance = balance
            
            return self.repository.update_member(member.member_id, member) > 0
            
        except Exception as e:
            print(f"更新会员失败: {e}")
            return False
    
    def update_balance(self, phone: str, new_balance: float) -> bool:
        """更新会员余额"""
        try:
            return self.repository.update_balance(phone, new_balance) > 0
        except Exception as e:
            print(f"更新会员余额失败: {e}")
            return False
    
    def add_balance(self, phone: str, amount: float) -> bool:
        """为会员增加余额"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # 获取当前余额
            cur.execute("SELECT balance FROM members WHERE phone = ?", (phone,))
            result = cur.fetchone()
            
            if not result:
                conn.close()
                return False
            
            current_balance = result[0]
            new_balance = current_balance + amount
            
            # 更新余额
            cur.execute(
                "UPDATE members SET balance = ? WHERE phone = ?",
                (new_balance, phone)
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"增加会员余额失败: {e}")
            return False
    
    def deduct_balance(self, phone: str, amount: float) -> bool:
        """从会员余额中扣款"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # 获取当前余额
            cur.execute("SELECT balance FROM members WHERE phone = ?", (phone,))
            result = cur.fetchone()
            
            if not result:
                conn.close()
                return False
            
            current_balance = result[0]
            
            # 检查余额是否足够
            if current_balance < amount:
                conn.close()
                return False
            
            new_balance = current_balance - amount
            
            # 更新余额
            cur.execute(
                "UPDATE members SET balance = ? WHERE phone = ?",
                (new_balance, phone)
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"扣款失败: {e}")
            return False
    
    def delete_member(self, phone: str) -> bool:
        """删除会员"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # 检查是否有关联的销售记录
            cur.execute(
                "SELECT COUNT(*) FROM sales WHERE member_phone = ?", 
                (phone,)
            )
            sales_count = cur.fetchone()[0]
            
            if sales_count > 0:
                # 有关联记录，不允许删除
                conn.close()
                return False
            
            # 删除会员
            cur.execute("DELETE FROM members WHERE phone = ?", (phone,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"删除会员失败: {e}")
            return False
    
    def get_member_statistics(self) -> Dict[str, Any]:
        """获取会员统计信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # 总会员数
            cur.execute("SELECT COUNT(*) FROM members")
            total_members = cur.fetchone()[0]
            
            # 今日新增会员
            today = date.today().strftime("%Y-%m-%d")
            cur.execute(
                "SELECT COUNT(*) FROM members WHERE join_date LIKE ?",
                (f"{today}%",)
            )
            today_new_members = cur.fetchone()[0]
            
            # 余额统计
            cur.execute("SELECT SUM(balance), AVG(balance) FROM members")
            balance_stats = cur.fetchone()
            total_balance = balance_stats[0] or 0
            avg_balance = balance_stats[1] or 0
            
            # 高余额会员数量
            cur.execute("SELECT COUNT(*) FROM members WHERE balance > 1000")
            high_balance_members = cur.fetchone()[0]
            
            conn.close()
            
            return {
                "total_members": total_members,
                "today_new_members": today_new_members,
                "total_balance": total_balance,
                "avg_balance": avg_balance,
                "high_balance_members": high_balance_members
            }
            
        except Exception as e:
            print(f"获取会员统计失败: {e}")
            return {}
    
    def get_top_members_by_balance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取余额最高的会员"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute(
                "SELECT phone, balance, remark, join_date FROM members "
                "ORDER BY balance DESC LIMIT ?",
                (limit,)
            )
            
            results = cur.fetchall()
            conn.close()
            
            return [
                {
                    "phone": row[0],
                    "balance": row[1],
                    "remark": row[2],
                    "join_date": row[3]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"获取高余额会员失败: {e}")
            return []
    
    def batch_import_members(self, members_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量导入会员"""
        success_count = 0
        error_count = 0
        duplicate_count = 0
        
        for member_data in members_data:
            try:
                phone = member_data.get("phone", "").strip()
                remark = member_data.get("remark", "")
                balance = float(member_data.get("balance", 0))
                
                if not phone:
                    error_count += 1
                    continue
                
                # 检查是否已存在
                if self.repository.find_by_phone(phone):
                    duplicate_count += 1
                    continue
                
                # 创建会员
                if self.create_member(phone, remark, balance):
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"导入会员失败 {member_data}: {e}")
                error_count += 1
        
        return {
            "success": success_count,
            "error": error_count,
            "duplicate": duplicate_count
        }
