#!/usr/bin/env python3
"""
姐妹花销售系统 - 完整版
基于模块化架构重构的销售管理系统 (已移除彩蛋功能)

主要功能：
1. 会员管理 - 会员注册、余额管理、统计查询
2. 库存管理 - 商品管理、分类管理、库存统计
3. 销售管理 - 销售记录、退款处理、销售统计
4. 目标管理 - 销售目标设置与跟踪
5. 备份管理 - 数据库备份与恢复
6. 数据分析 - 销售报表、热门商品分析

作者: MiniMax Agent
版本: 2.0 完整版 (无彩蛋)
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主程序入口"""
    print("🌸 姐妹花销售系统 - 完整版启动中...")
    print("=" * 50)
    
    try:
        # 1. 初始化配置
        from config.settings import load_config, AppConfig
        config = load_config()
        print("✅ 配置管理模块加载成功")
        
        # 2. 初始化数据库
        from database.initializer import init_db
        init_db()
        print("✅ 数据库访问层初始化成功")
        
        # 3. 初始化业务服务
        from services.member_service import MemberService
        from services.inventory_service import InventoryService  
        from services.sales_service import SalesService
        from services.other_services import GoalService, PushService, BackupService
        print("✅ 业务服务层初始化成功")
        
        # 4. 启动GUI
        print("🚀 正在启动GUI界面...")
        root = tk.Tk()
        app = SalesManagementSystem(root)
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False


class SalesManagementSystem:
    """销售管理系统主界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("姐妹花销售系统 - 完整版")
        self.root.geometry("1200x800")
        
        # 初始化服务
        self.member_service = MemberService()
        self.inventory_service = InventoryService()
        self.sales_service = SalesService()
        self.goal_service = GoalService()
        self.backup_service = BackupService()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化默认数据
        self.initialize_default_data()
        
    def create_widgets(self):
        """创建主界面组件"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 销售管理页面
        self.create_sales_tab()
        
        # 会员管理页面
        self.create_member_tab()
        
        # 库存管理页面
        self.create_inventory_tab()
        
        # 数据统计页面
        self.create_statistics_tab()
        
        # 系统管理页面
        self.create_system_tab()
        
    def create_sales_tab(self):
        """创建销售管理标签页"""
        sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_frame, text="销售管理")
        
        # 今日销售概览
        overview_frame = ttk.LabelFrame(sales_frame, text="今日销售概览")
        overview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sales_var = tk.StringVar(value="今日销售额: 0.00元")
        ttk.Label(overview_frame, textvariable=self.sales_var, font=("Arial", 12, "bold")).pack(pady=10)
        
        # 快速销售
        quick_frame = ttk.LabelFrame(sales_frame, text="快速销售")
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 会员选择
        ttk.Label(quick_frame, text="会员手机号:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.member_phone_var = tk.StringVar()
        self.member_entry = ttk.Entry(quick_frame, textvariable=self.member_phone_var, width=20)
        self.member_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 商品选择
        ttk.Label(quick_frame, text="商品名称:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.item_name_var = tk.StringVar()
        self.item_entry = ttk.Entry(quick_frame, textvariable=self.item_name_var, width=20)
        self.item_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 数量
        ttk.Label(quick_frame, text="数量:").grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = ttk.Entry(quick_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 销售按钮
        ttk.Button(quick_frame, text="确认销售", command=self.quick_sale).grid(row=0, column=6, padx=10, pady=5)
        
        # 今日销售记录
        records_frame = ttk.LabelFrame(sales_frame, text="今日销售记录")
        records_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 销售记录表格
        columns = ("时间", "会员", "商品", "数量", "金额")
        self.sales_tree = ttk.Treeview(records_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=150)
        
        # 滚动条
        sales_scrollbar = ttk.Scrollbar(records_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sales_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新今日销售
        self.refresh_today_sales()
        
    def create_member_tab(self):
        """创建会员管理标签页"""
        member_frame = ttk.Frame(self.notebook)
        self.notebook.add(member_frame, text="会员管理")
        
        # 会员操作
        op_frame = ttk.LabelFrame(member_frame, text="会员操作")
        op_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(op_frame, text="新增会员", command=self.add_member).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(op_frame, text="会员充值", command=self.member_recharge).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(op_frame, text="查询会员", command=self.query_member).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 会员列表
        list_frame = ttk.LabelFrame(member_frame, text="会员列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 会员表格
        member_columns = ("手机号", "余额", "备注", "注册日期")
        self.member_tree = ttk.Treeview(list_frame, columns=member_columns, show="headings")
        
        for col in member_columns:
            self.member_tree.heading(col, text=col)
            self.member_tree.column(col, width=150)
        
        member_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.member_tree.yview)
        self.member_tree.configure(yscrollcommand=member_scrollbar.set)
        
        self.member_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        member_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新会员列表
        self.refresh_member_list()
        
    def create_inventory_tab(self):
        """创建库存管理标签页"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="库存管理")
        
        # 库存操作
        op_frame = ttk.LabelFrame(inventory_frame, text="商品操作")
        op_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(op_frame, text="新增商品", command=self.add_item).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(op_frame, text="编辑商品", command=self.edit_item).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(op_frame, text="删除商品", command=self.delete_item).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 库存列表
        list_frame = ttk.LabelFrame(inventory_frame, text="商品库存")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 商品表格
        item_columns = ("商品名称", "分类", "价格", "会员价", "备注")
        self.item_tree = ttk.Treeview(list_frame, columns=item_columns, show="headings")
        
        for col in item_columns:
            self.item_tree.heading(col, text=col)
            self.item_tree.column(col, width=150)
        
        item_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.item_tree.yview)
        self.item_tree.configure(yscrollcommand=item_scrollbar.set)
        
        self.item_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        item_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新商品列表
        self.refresh_item_list()
        
    def create_statistics_tab(self):
        """创建数据统计标签页"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="数据统计")
        
        # 今日统计
        today_frame = ttk.LabelFrame(stats_frame, text="今日数据")
        today_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_var = tk.StringVar(value="今日销售额: 0.00元")
        ttk.Label(today_frame, textvariable=self.stats_var, font=("Arial", 12, "bold")).pack(pady=10)
        
        # 销售目标
        goal_frame = ttk.LabelFrame(stats_frame, text="销售目标")
        goal_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(goal_frame, text="设置目标", command=self.set_goals).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.goal_var = tk.StringVar(value="今日目标: 1000.00元")
        ttk.Label(goal_frame, textvariable=self.goal_var, font=("Arial", 10)).pack(side=tk.LEFT, padx=20, pady=5)
        
        # 热门商品
        hot_frame = ttk.LabelFrame(stats_frame, text="热门商品")
        hot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 热门商品表格
        hot_columns = ("商品名称", "分类", "销量", "销售额")
        self.hot_tree = ttk.Treeview(hot_frame, columns=hot_columns, show="headings")
        
        for col in hot_columns:
            self.hot_tree.heading(col, text=col)
            self.hot_tree.column(col, width=150)
        
        hot_scrollbar = ttk.Scrollbar(hot_frame, orient=tk.VERTICAL, command=self.hot_tree.yview)
        self.hot_tree.configure(yscrollcommand=hot_scrollbar.set)
        
        self.hot_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hot_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新统计数据
        self.refresh_statistics()
        
    def create_system_tab(self):
        """创建系统管理标签页"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="系统管理")
        
        # 系统操作
        op_frame = ttk.LabelFrame(system_frame, text="系统操作")
        op_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(op_frame, text="创建备份", command=self.create_backup).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(op_frame, text="系统信息", command=self.show_system_info).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(op_frame, text="退出系统", command=self.quit_system).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 系统信息显示
        info_frame = ttk.LabelFrame(system_frame, text="系统信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        info_text = tk.Text(info_frame, height=20)
        info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 插入系统信息
        system_info = """
姐妹花销售系统 - 完整版

主要功能：
• 销售管理：快速销售、销售记录、退款处理
• 会员管理：会员注册、余额管理、查询统计
• 库存管理：商品管理、分类管理、库存统计
• 数据分析：销售报表、热门商品、目标跟踪
• 系统管理：备份恢复、系统设置

系统特点：
• 模块化架构设计
• 完整的业务逻辑
• 友好的用户界面
• 数据安全备份
• 实时数据统计

版本：2.0 完整版
作者：MiniMax Agent
        """
        info_text.insert(tk.END, system_info)
        info_text.config(state=tk.DISABLED)
        
    def initialize_default_data(self):
        """初始化默认数据"""
        # 添加默认商品
        default_items = [
            ("玫瑰花", "花卉", 10.0, 8.0, "红色玫瑰"),
            ("康乃馨", "花卉", 8.0, 6.0, "粉色康乃馨"),
            ("百合花", "花卉", 15.0, 12.0, "白色百合"),
            ("向日葵", "花卉", 12.0, 10.0, "黄色向日葵"),
            ("包装纸", "包装", 2.0, 2.0, "彩色包装纸"),
            ("花束包装", "服务", 5.0, 5.0, "专业包装服务")
        ]
        
        for item in default_items:
            if not self.inventory_service.get_item_by_name(item[0]):
                self.inventory_service.create_item(*item)
        
        # 刷新所有数据
        self.refresh_all_data()
        
    def refresh_all_data(self):
        """刷新所有数据"""
        self.refresh_today_sales()
        self.refresh_member_list()
        self.refresh_item_list()
        self.refresh_statistics()
        
    def refresh_today_sales(self):
        """刷新今日销售数据"""
        # 清空表格
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # 获取今日销售记录
        today_sales = self.sales_service.get_today_sales()
        total_sales = 0
        
        for sale in today_sales:
            # 获取销售明细
            from database.manager import db_manager
            items = db_manager.fetch_all(
                "SELECT si.name, si.quantity, si.price * si.quantity FROM sale_items si WHERE sale_id = ?",
                (sale.sale_id,)
            )
            
            for item_name, quantity, amount in items:
                member = sale.member_phone if sale.is_member else "散客"
                self.sales_tree.insert("", tk.END, values=(
                    sale.datetime[:16], member, item_name, quantity, f"{amount:.2f}"
                ))
                total_sales += amount
        
        self.sales_var.set(f"今日销售额: {total_sales:.2f}元")
        
    def refresh_member_list(self):
        """刷新会员列表"""
        # 清空表格
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        
        # 获取会员列表
        members = self.member_service.get_all_members()
        
        for member in members:
            self.member_tree.insert("", tk.END, values=(
                member.phone, f"{member.balance:.2f}", member.remark, member.join_date[:10]
            ))
            
    def refresh_item_list(self):
        """刷新商品列表"""
        # 清空表格
        for item in self.item_tree.get_children():
            self.item_tree.delete(item)
        
        # 获取商品列表
        items = self.inventory_service.get_all_items()
        
        for item in items:
            self.item_tree.insert("", tk.END, values=(
                item.name, item.category, f"{item.price:.2f}", f"{item.member_price:.2f}", item.remark
            ))
            
    def refresh_statistics(self):
        """刷新统计数据"""
        # 获取今日销售统计
        stats = self.sales_service.get_sales_statistics()
        self.stats_var.set(f"今日销售额: {stats['total_sales']:.2f}元 (会员: {stats['member_sales']:.2f}元, 散客: {stats['cash_sales']:.2f}元)")
        
        # 获取销售目标
        day_goal, month_goal = self.goal_service.get_current_goals()
        progress = self.goal_service.get_progress()
        day_progress = progress['day_progress']
        self.goal_var.set(f"今日目标: {day_goal:.2f}元 (完成: {day_progress['percentage']:.1f}%)")
        
        # 清空热门商品表格
        for item in self.hot_tree.get_children():
            self.hot_tree.delete(item)
        
        # 获取热门商品
        hot_items = self.sales_service.get_top_selling_items(10)
        
        for item in hot_items:
            self.hot_tree.insert("", tk.END, values=(
                item['name'], item['category'], item['total_quantity'], f"{item['total_revenue']:.2f}"
            ))
            
    def quick_sale(self):
        """快速销售"""
        try:
            member_phone = self.member_phone_var.get().strip()
            item_name = self.item_name_var.get().strip()
            quantity = int(self.quantity_var.get() or "1")
            
            if not item_name:
                messagebox.showerror("错误", "请输入商品名称")
                return
            
            # 获取商品信息
            item = self.inventory_service.get_item_by_name(item_name)
            if not item:
                messagebox.showerror("错误", "商品不存在")
                return
            
            # 检查会员
            member = None
            is_member = False
            if member_phone:
                member = self.member_service.get_member_by_phone(member_phone)
                if not member:
                    messagebox.showerror("错误", "会员不存在")
                    return
                is_member = True
                price = item.member_price
            else:
                price = item.price
            
            # 计算金额
            total_amount = price * quantity
            
            # 确认销售
            confirm_msg = f"""
销售确认：
商品: {item_name}
价格: {price:.2f}元
数量: {quantity}
总金额: {total_amount:.2f}元
{"会员: " + member_phone if is_member else "散客"}
            """
            
            if messagebox.askyesno("确认销售", confirm_msg):
                # 创建销售记录
                items = [{
                    "name": item_name,
                    "category": item.category,
                    "price": price,
                    "quantity": quantity,
                    "remark": ""
                }]
                
                sale_id = self.sales_service.create_sale(
                    items=items,
                    is_member=is_member,
                    member_phone=member_phone,
                    total_due=total_amount,
                    total_paid=total_amount
                )
                
                if sale_id:
                    messagebox.showinfo("成功", "销售完成！")
                    # 清空输入
                    self.member_phone_var.set("")
                    self.item_name_var.set("")
                    self.quantity_var.set("1")
                    # 刷新数据
                    self.refresh_all_data()
                else:
                    messagebox.showerror("错误", "销售失败")
                    
        except ValueError:
            messagebox.showerror("错误", "数量输入有误")
        except Exception as e:
            messagebox.showerror("错误", f"销售异常: {e}")
            
    def add_member(self):
        """添加会员"""
        dialog = MemberDialog(self.root, "添加会员", self.member_service)
        if dialog.result:
            self.refresh_member_list()
            messagebox.showinfo("成功", "会员添加成功！")
            
    def member_recharge(self):
        """会员充值"""
        dialog = RechargeDialog(self.root, "会员充值", self.member_service)
        if dialog.result:
            self.refresh_member_list()
            messagebox.showinfo("成功", "充值完成！")
            
    def query_member(self):
        """查询会员"""
        phone = tk.simpledialog.askstring("查询会员", "请输入会员手机号:")
        if phone:
            member = self.member_service.get_member_by_phone(phone)
            if member:
                info = f"""
会员信息：
手机号: {member.phone}
余额: {member.balance:.2f}元
备注: {member.remark}
注册日期: {member.join_date[:10]}
                """
                messagebox.showinfo("会员信息", info)
            else:
                messagebox.showerror("错误", "会员不存在")
                
    def add_item(self):
        """添加商品"""
        dialog = ItemDialog(self.root, "添加商品", self.inventory_service)
        if dialog.result:
            self.refresh_item_list()
            messagebox.showinfo("成功", "商品添加成功！")
            
    def edit_item(self):
        """编辑商品"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要编辑的商品")
            return
        
        item_name = self.item_tree.item(selected[0])['values'][0]
        item = self.inventory_service.get_item_by_name(item_name)
        if item:
            dialog = ItemDialog(self.root, "编辑商品", self.inventory_service, item)
            if dialog.result:
                self.refresh_item_list()
                messagebox.showinfo("成功", "商品更新成功！")
        else:
            messagebox.showerror("错误", "商品不存在")
            
    def delete_item(self):
        """删除商品"""
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请选择要删除的商品")
            return
        
        item_name = self.item_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("确认删除", f"确定要删除商品 '{item_name}' 吗？"):
            if self.inventory_service.delete_item(item_name):
                self.refresh_item_list()
                messagebox.showinfo("成功", "商品删除成功！")
            else:
                messagebox.showerror("错误", "删除失败（可能有关联记录）")
                
    def set_goals(self):
        """设置销售目标"""
        dialog = GoalDialog(self.root, "设置销售目标", self.goal_service)
        if dialog.result:
            self.refresh_statistics()
            messagebox.showinfo("成功", "目标设置成功！")
            
    def create_backup(self):
        """创建备份"""
        try:
            backup_file = self.backup_service.create_backup()
            if backup_file:
                messagebox.showinfo("成功", f"备份创建成功：{backup_file}")
            else:
                messagebox.showerror("错误", "备份创建失败")
        except Exception as e:
            messagebox.showerror("错误", f"备份异常: {e}")
            
    def show_system_info(self):
        """显示系统信息"""
        info = f"""
姐妹花销售系统 - 完整版
版本: 2.0
作者: MiniMax Agent

当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
系统状态: 运行正常

数据统计：
• 会员数量: {len(self.member_service.get_all_members())}
• 商品数量: {len(self.inventory_service.get_all_items())}
• 今日销售: {self.sales_service.get_sales_statistics()['sales_count']}笔

功能模块：
✓ 销售管理
✓ 会员管理  
✓ 库存管理
✓ 数据统计
✓ 系统管理
        """
        messagebox.showinfo("系统信息", info)
        
    def quit_system(self):
        """退出系统"""
        if messagebox.askyesno("确认退出", "确定要退出系统吗？"):
            self.root.quit()


class MemberDialog:
    """会员对话框"""
    
    def __init__(self, parent, title, member_service):
        self.member_service = member_service
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 输入控件
        ttk.Label(self.dialog, text="手机号:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.phone_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.phone_var, width=20).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="初始余额:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.balance_var = tk.StringVar(value="0.00")
        ttk.Entry(self.dialog, textvariable=self.balance_var, width=20).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="备注:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.remark_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.remark_var, width=20).grid(row=2, column=1, padx=10, pady=10)
        
        # 按钮
        ttk.Button(self.dialog, text="确定", command=self.save).grid(row=3, column=0, padx=10, pady=20)
        ttk.Button(self.dialog, text="取消", command=self.cancel).grid(row=3, column=1, padx=10, pady=20)
        
        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
    def save(self):
        """保存"""
        try:
            phone = self.phone_var.get().strip()
            balance = float(self.balance_var.get() or "0")
            remark = self.remark_var.get().strip()
            
            if not phone:
                messagebox.showerror("错误", "请输入手机号")
                return
            
            if self.member_service.create_member(phone, remark, balance):
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "手机号已存在或创建失败")
                
        except ValueError:
            messagebox.showerror("错误", "余额输入有误")
        except Exception as e:
            messagebox.showerror("错误", f"保存异常: {e}")
            
    def cancel(self):
        """取消"""
        self.dialog.destroy()


class RechargeDialog:
    """会员充值对话框"""
    
    def __init__(self, parent, title, member_service):
        self.member_service = member_service
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 输入控件
        ttk.Label(self.dialog, text="会员手机号:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.phone_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.phone_var, width=20).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="充值金额:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.amount_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.amount_var, width=20).grid(row=1, column=1, padx=10, pady=10)
        
        # 按钮
        ttk.Button(self.dialog, text="确定", command=self.save).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(self.dialog, text="取消", command=self.cancel).grid(row=2, column=1, padx=10, pady=20)
        
    def save(self):
        """保存"""
        try:
            phone = self.phone_var.get().strip()
            amount = float(self.amount_var.get())
            
            if not phone:
                messagebox.showerror("错误", "请输入会员手机号")
                return
            
            member = self.member_service.get_member_by_phone(phone)
            if not member:
                messagebox.showerror("错误", "会员不存在")
                return
            
            if self.member_service.add_balance(phone, amount):
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "充值失败")
                
        except ValueError:
            messagebox.showerror("错误", "金额输入有误")
        except Exception as e:
            messagebox.showerror("错误", f"充值异常: {e}")
            
    def cancel(self):
        """取消"""
        self.dialog.destroy()


class ItemDialog:
    """商品对话框"""
    
    def __init__(self, parent, title, inventory_service, item=None):
        self.inventory_service = inventory_service
        self.result = False
        self.item = item
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 输入控件
        ttk.Label(self.dialog, text="商品名称:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.name_var = tk.StringVar(value=item.name if item else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="商品分类:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.category_var = tk.StringVar(value=item.category if item else "")
        ttk.Entry(self.dialog, textvariable=self.category_var, width=20).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="价格:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.price_var = tk.StringVar(value=str(item.price) if item else "0.00")
        ttk.Entry(self.dialog, textvariable=self.price_var, width=20).grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="会员价:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.member_price_var = tk.StringVar(value=str(item.member_price) if item else "0.00")
        ttk.Entry(self.dialog, textvariable=self.member_price_var, width=20).grid(row=3, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="备注:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.remark_var = tk.StringVar(value=item.remark if item else "")
        ttk.Entry(self.dialog, textvariable=self.remark_var, width=20).grid(row=4, column=1, padx=10, pady=10)
        
        # 按钮
        ttk.Button(self.dialog, text="确定", command=self.save).grid(row=5, column=0, padx=10, pady=20)
        ttk.Button(self.dialog, text="取消", command=self.cancel).grid(row=5, column=1, padx=10, pady=20)
        
    def save(self):
        """保存"""
        try:
            name = self.name_var.get().strip()
            category = self.category_var.get().strip()
            price = float(self.price_var.get())
            member_price = float(self.member_price_var.get())
            remark = self.remark_var.get().strip()
            
            if not name:
                messagebox.showerror("错误", "请输入商品名称")
                return
            
            if self.item:
                # 更新商品
                if self.inventory_service.update_item(name, category, price, member_price, remark):
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("错误", "更新失败")
            else:
                # 新增商品
                if self.inventory_service.create_item(name, category, price, member_price, remark):
                    self.result = True
                    self.dialog.destroy()
                else:
                    messagebox.showerror("错误", "商品已存在或创建失败")
                
        except ValueError:
            messagebox.showerror("错误", "价格输入有误")
        except Exception as e:
            messagebox.showerror("错误", f"保存异常: {e}")
            
    def cancel(self):
        """取消"""
        self.dialog.destroy()


class GoalDialog:
    """目标设置对话框"""
    
    def __init__(self, parent, title, goal_service):
        self.goal_service = goal_service
        self.result = False
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 获取当前目标
        day_goal, month_goal = self.goal_service.get_current_goals()
        
        # 输入控件
        ttk.Label(self.dialog, text="今日目标:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.day_goal_var = tk.StringVar(value=str(day_goal))
        ttk.Entry(self.dialog, textvariable=self.day_goal_var, width=20).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(self.dialog, text="本月目标:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.month_goal_var = tk.StringVar(value=str(month_goal))
        ttk.Entry(self.dialog, textvariable=self.month_goal_var, width=20).grid(row=1, column=1, padx=10, pady=10)
        
        # 按钮
        ttk.Button(self.dialog, text="确定", command=self.save).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(self.dialog, text="取消", command=self.cancel).grid(row=2, column=1, padx=10, pady=20)
        
    def save(self):
        """保存"""
        try:
            day_goal = float(self.day_goal_var.get())
            month_goal = float(self.month_goal_var.get())
            
            self.goal_service.set_goals(day_goal, month_goal)
            self.result = True
            self.dialog.destroy()
                
        except ValueError:
            messagebox.showerror("错误", "目标金额输入有误")
        except Exception as e:
            messagebox.showerror("错误", f"保存异常: {e}")
            
    def cancel(self):
        """取消"""
        self.dialog.destroy()


if __name__ == "__main__":
    # 运行主程序
    success = main()
    
    if success:
        print("\n🌟 姐妹花销售系统启动成功！")
        print("💡 提示：程序已移除所有彩蛋功能，提供纯净的销售管理体验")
    else:
        print("\n❌ 启动失败，请检查错误信息。")
        sys.exit(1)