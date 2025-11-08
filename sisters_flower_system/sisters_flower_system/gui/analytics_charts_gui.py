"""
数据分析图表模块
提供完整的数据分析和图表展示功能
"""

import os
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# 数据库和业务服务模块的占位符导入
# 在实际使用时可以取消注释下面的导入
# try:
#     from ..database.manager import DatabaseManager
#     from ..services.sales_service import SalesService
#     from ..services.inventory_service import InventoryService
#     from ..services.member_service import MemberService
# except ImportError:
#     # 直接导入
#     import sys
#     import os
#     sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     from database.manager import DatabaseManager
#     from services.sales_service import SalesService
#     from services.inventory_service import InventoryService
#     from services.member_service import MemberService

try:
    from .base_components import BaseFrame, BaseLabel, BaseButton, BaseTreeview
except ImportError:
    from base_components import BaseFrame, BaseLabel, BaseButton, BaseTreeview


class ChartManager:
    """图表管理器"""
    
    def __init__(self):
        self.charts = {}
        self.data_cache = {}
        
    def get_sales_data(self, days: int = 30) -> Dict[str, Any]:
        """获取销售数据"""
        # 模拟数据 - 实际应用中从数据库获取
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             end=datetime.now(), freq='D')
        
        # 生成模拟销售数据
        np.random.seed(42)
        daily_sales = np.random.normal(5000, 1500, len(dates))
        daily_sales = np.maximum(daily_sales, 1000)  # 最小销售额1000
        
        return {
            'dates': dates,
            'sales': daily_sales,
            'total': sum(daily_sales),
            'average': np.mean(daily_sales)
        }
    
    def get_product_sales_data(self, top_n: int = 10) -> Dict[str, Any]:
        """获取商品销售数据"""
        # 模拟数据
        products = ['玫瑰', '康乃馨', '向日葵', '百合', '郁金香', 
                   '满天星', '非洲菊', '紫罗兰', '薰衣草', '勿忘我']
        sales_data = np.random.randint(100, 1000, len(products))
        
        # 排序并取前N名
        sorted_data = sorted(zip(products, sales_data), key=lambda x: x[1], reverse=True)[:top_n]
        products, sales_data = zip(*sorted_data)
        
        return {
            'products': list(products),
            'sales': list(sales_data),
            'total': sum(sales_data)
        }
    
    def get_customer_data(self) -> Dict[str, Any]:
        """获取客户分析数据"""
        # 模拟客户数据
        customer_types = ['新客户', '老客户', 'VIP客户', '普通客户']
        customer_counts = np.random.randint(50, 200, len(customer_types))
        
        return {
            'types': customer_types,
            'counts': customer_counts,
            'total': sum(customer_counts)
        }
    
    def get_inventory_data(self) -> Dict[str, Any]:
        """获取库存分析数据"""
        # 模拟库存数据
        products = ['玫瑰', '康乃馨', '向日葵', '百合', '郁金香', 
                   '满天星', '非洲菊', '紫罗兰', '薰衣草', '勿忘我']
        current_stock = np.random.randint(10, 100, len(products))
        min_stock = [20] * len(products)  # 最低库存
        max_stock = [200] * len(products)  # 最高库存
        
        return {
            'products': products,
            'current_stock': current_stock,
            'min_stock': min_stock,
            'max_stock': max_stock,
            'low_stock_items': [p for p, s in zip(products, current_stock) if s < 20]
        }
    
    def get_financial_data(self, months: int = 12) -> Dict[str, Any]:
        """获取财务数据"""
        # 模拟财务数据
        months_list = pd.date_range(start=datetime.now() - timedelta(days=months*30), 
                                   end=datetime.now(), freq='ME')
        
        np.random.seed(123)
        revenue = np.random.normal(50000, 15000, len(months_list))
        expenses = np.random.normal(30000, 10000, len(months_list))
        profit = revenue - expenses
        
        return {
            'months': months_list,
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'total_revenue': sum(revenue),
            'total_expenses': sum(expenses),
            'total_profit': sum(profit)
        }


class AnalyticsChartsGUI(BaseFrame):
    """数据分析图表主界面"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.chart_manager = ChartManager()
        self.current_chart_type = tk.StringVar(value="sales_trend")
        self.auto_refresh = False
        self.refresh_interval = 30  # 秒
        self.charts = {}
        self.setup_ui()
        self.start_auto_refresh()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        self.main_frame = ttk.Frame(self.widget)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 顶部控制面板
        self.setup_control_panel()
        
        # 图表显示区域
        self.setup_chart_area()
        
        # 底部操作面板
        self.setup_action_panel()
        
        # 初始化图表
        self.update_chart()
    
    def setup_control_panel(self):
        """设置控制面板"""
        control_frame = ttk.LabelFrame(self.main_frame, text="图表控制", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # 图表类型选择
        ttk.Label(control_frame, text="图表类型:").grid(row=0, column=0, padx=(0, 5))
        
        chart_types = [
            ("销售趋势", "sales_trend"),
            ("商品销售占比", "product_sales"),
            ("客户分析", "customer_analysis"),
            ("库存分析", "inventory_analysis"),
            ("财务报表", "financial_report")
        ]
        
        for i, (text, value) in enumerate(chart_types):
            ttk.Radiobutton(control_frame, text=text, value=value, 
                           variable=self.current_chart_type,
                           command=self.update_chart).grid(row=0, column=i+1, padx=5)
        
        # 时间范围选择
        ttk.Label(control_frame, text="时间范围:").grid(row=1, column=0, padx=(0, 5), pady=(10, 0))
        
        self.time_range = ttk.Combobox(control_frame, values=["7天", "30天", "90天", "1年"], 
                                      state="readonly", width=10)
        self.time_range.set("30天")
        self.time_range.grid(row=1, column=1, padx=5, pady=(10, 0))
        
        # 自动刷新控制
        self.auto_refresh_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="自动刷新", variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).grid(row=1, column=2, padx=5, pady=(10, 0))
        
        ttk.Label(control_frame, text="刷新间隔(秒):").grid(row=1, column=3, padx=(5, 5), pady=(10, 0))
        self.refresh_interval_var = ttk.Entry(control_frame, width=8)
        self.refresh_interval_var.insert(0, "30")
        self.refresh_interval_var.grid(row=1, column=4, padx=5, pady=(10, 0))
    
    def setup_chart_area(self):
        """设置图表显示区域"""
        chart_frame = ttk.LabelFrame(self.main_frame, text="数据分析图表", padding=10)
        chart_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 图表容器
        self.chart_container = ttk.Frame(chart_frame)
        self.chart_container.pack(fill='both', expand=True)
        
        # 创建matplotlib图形
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.1, wspace=0.3, hspace=0.3)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_container)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # 绑定事件
        self.canvas.mpl_connect('button_press_event', self.on_chart_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_chart_hover)
    
    def setup_action_panel(self):
        """设置操作面板"""
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill='x')
        
        # 左侧操作按钮
        left_frame = ttk.Frame(action_frame)
        left_frame.pack(side='left')
        
        ttk.Button(left_frame, text="刷新数据", command=self.update_chart).pack(side='left', padx=(0, 5))
        ttk.Button(left_frame, text="重置图表", command=self.reset_chart).pack(side='left', padx=5)
        ttk.Button(left_frame, text="全屏显示", command=self.fullscreen_chart).pack(side='left', padx=5)
        
        # 右侧导出按钮
        right_frame = ttk.Frame(action_frame)
        right_frame.pack(side='right')
        
        ttk.Button(right_frame, text="导出PNG", command=lambda: self.export_chart('png')).pack(side='left', padx=5)
        ttk.Button(right_frame, text="导出PDF", command=lambda: self.export_chart('pdf')).pack(side='left', padx=5)
        ttk.Button(right_frame, text="导出Excel", command=self.export_excel).pack(side='left', padx=5)
        ttk.Button(right_frame, text="打印", command=self.print_chart).pack(side='left', padx=5)
    
    def update_chart(self):
        """更新图表"""
        self.fig.clear()
        
        chart_type = self.current_chart_type.get()
        time_range = self.time_range.get()
        
        # 解析时间范围
        days = 30
        if "7天" in time_range:
            days = 7
        elif "90天" in time_range:
            days = 90
        elif "1年" in time_range:
            days = 365
        
        try:
            if chart_type == "sales_trend":
                self.create_sales_trend_chart(days)
            elif chart_type == "product_sales":
                self.create_product_sales_chart()
            elif chart_type == "customer_analysis":
                self.create_customer_analysis_chart()
            elif chart_type == "inventory_analysis":
                self.create_inventory_analysis_chart()
            elif chart_type == "financial_report":
                self.create_financial_report_chart(days//30)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"更新图表失败: {str(e)}")
    
    def create_sales_trend_chart(self, days: int):
        """创建销售趋势图表"""
        data = self.chart_manager.get_sales_data(days)
        
        # 创建子图
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax3 = self.fig.add_subplot(2, 1, 2)
        
        # 折线图 - 销售趋势
        ax1.plot(data['dates'], data['sales'], marker='o', linewidth=2, markersize=4)
        ax1.set_title('销售趋势 - 折线图', fontsize=14, fontweight='bold')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('销售额 (元)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 柱状图 - 销售趋势
        ax2.bar(range(len(data['sales'])), data['sales'], color='skyblue', alpha=0.7)
        ax2.set_title('销售趋势 - 柱状图', fontsize=14, fontweight='bold')
        ax2.set_xlabel('天数')
        ax2.set_ylabel('销售额 (元)')
        ax2.grid(True, alpha=0.3)
        
        # 销售统计信息
        ax3.axis('off')
        stats_text = f"""
        销售统计信息
        
        总销售额: {data['total']:,.0f} 元
        平均日销售额: {data['average']:,.0f} 元
        最高日销售额: {max(data['sales']):,.0f} 元
        最低日销售额: {min(data['sales']):,.0f} 元
        数据天数: {len(data['dates'])} 天
        """
        ax3.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    
    def create_product_sales_chart(self):
        """创建商品销售占比图表"""
        data = self.chart_manager.get_product_sales_data()
        
        # 创建子图
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax3 = self.fig.add_subplot(2, 1, 2)
        
        # 饼图 - 商品销售占比
        colors = plt.cm.Set3(np.linspace(0, 1, len(data['products'])))
        wedges, texts, autotexts = ax1.pie(data['sales'], labels=data['products'], autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('商品销售占比 - 饼图', fontsize=14, fontweight='bold')
        
        # 环形图 - 商品销售占比
        wedges2, texts2, autotexts2 = ax2.pie(data['sales'], labels=data['products'], autopct='%1.1f%%',
                                             colors=colors, startangle=90, wedgeprops=dict(width=0.5))
        ax2.set_title('商品销售占比 - 环形图', fontsize=14, fontweight='bold')
        
        # 商品销售排行
        y_pos = np.arange(len(data['products']))
        ax3.barh(y_pos, data['sales'], color='lightgreen', alpha=0.7)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(data['products'])
        ax3.set_xlabel('销售数量')
        ax3.set_title('商品销售排行', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # 添加数值标签
        for i, v in enumerate(data['sales']):
            ax3.text(v + 0.01*max(data['sales']), i, str(v), va='center', ha='left')
    
    def create_customer_analysis_chart(self):
        """创建客户分析图表"""
        data = self.chart_manager.get_customer_data()
        
        # 创建子图
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax3 = self.fig.add_subplot(2, 1, 2)
        
        # 饼图 - 客户类型分布
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        wedges, texts, autotexts = ax1.pie(data['counts'], labels=data['types'], autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('客户类型分布', fontsize=14, fontweight='bold')
        
        # 柱状图 - 客户数量
        bars = ax2.bar(data['types'], data['counts'], color=colors, alpha=0.7)
        ax2.set_title('客户数量统计', fontsize=14, fontweight='bold')
        ax2.set_ylabel('客户数量')
        ax2.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 客户分析统计
        ax3.axis('off')
        total_customers = data['total']
        stats_text = f"""
        客户分析统计
        
        总客户数: {total_customers} 人
        平均客户数: {total_customers/len(data['types']):.0f} 人/类型
        最大客户群体: {data['types'][np.argmax(data['counts'])]}
        最大群体人数: {max(data['counts'])} 人
        """
        ax3.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.7))
    
    def create_inventory_analysis_chart(self):
        """创建库存分析图表"""
        data = self.chart_manager.get_inventory_data()
        
        # 创建子图
        ax1 = self.fig.add_subplot(2, 2, (1, 2))
        ax2 = self.fig.add_subplot(2, 2, 3)
        ax3 = self.fig.add_subplot(2, 2, 4)
        
        # 库存状态图
        x = np.arange(len(data['products']))
        width = 0.25
        
        ax1.bar(x - width, data['current_stock'], width, label='当前库存', alpha=0.8)
        ax1.bar(x, data['min_stock'], width, label='最低库存', alpha=0.8)
        ax1.bar(x + width, data['max_stock'], width, label='最高库存', alpha=0.8)
        
        ax1.set_title('库存状态分析', fontsize=14, fontweight='bold')
        ax1.set_ylabel('库存数量')
        ax1.set_xticks(x)
        ax1.set_xticklabels(data['products'], rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 库存预警
        low_stock_colors = ['red' if stock < 20 else 'blue' for stock in data['current_stock']]
        bars = ax2.bar(data['products'], data['current_stock'], color=low_stock_colors, alpha=0.7)
        ax2.set_title('库存预警', fontsize=14, fontweight='bold')
        ax2.set_ylabel('当前库存')
        ax2.tick_params(axis='x', rotation=45)
        
        # 添加预警线
        ax2.axhline(y=20, color='red', linestyle='--', label='预警线')
        ax2.legend()
        
        # 库存统计
        ax3.axis('off')
        total_items = len(data['products'])
        low_stock_count = len(data['low_stock_items'])
        total_stock = sum(data['current_stock'])
        
        stats_text = f"""
        库存统计信息
        
        商品种类: {total_items} 种
        预警商品: {low_stock_count} 种
        总库存量: {total_stock} 件
        预警商品列表:
        {', '.join(data['low_stock_items'])}
        """
        ax3.text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))
    
    def create_financial_report_chart(self, months: int):
        """创建财务报表图表"""
        data = self.chart_manager.get_financial_data(months)
        
        # 创建子图
        ax1 = self.fig.add_subplot(2, 2, 1)
        ax2 = self.fig.add_subplot(2, 2, 2)
        ax3 = self.fig.add_subplot(2, 1, 2)
        
        # 收入和支出趋势
        ax1.plot(data['months'], data['revenue'], marker='o', label='收入', linewidth=2)
        ax1.plot(data['months'], data['expenses'], marker='s', label='支出', linewidth=2)
        ax1.set_title('收支趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('金额 (元)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 利润趋势
        ax2.fill_between(data['months'], data['profit'], alpha=0.3, color='green')
        ax2.plot(data['months'], data['profit'], marker='o', color='green', linewidth=2)
        ax2.set_title('利润趋势', fontsize=14, fontweight='bold')
        ax2.set_ylabel('利润 (元)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 财务统计
        ax3.axis('off')
        profit_margin = (data['total_profit'] / data['total_revenue']) * 100
        
        stats_text = f"""
        财务统计信息
        
        总收入: {data['total_revenue']:,.0f} 元
        总支出: {data['total_expenses']:,.0f} 元
        总利润: {data['total_profit']:,.0f} 元
        利润率: {profit_margin:.2f}%
        平均月收入: {data['total_revenue']/months:,.0f} 元
        平均月支出: {data['total_expenses']/months:,.0f} 元
        """
        ax3.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
    
    def on_chart_click(self, event):
        """图表点击事件"""
        if event.inaxes:
            x, y = event.xdata, event.ydata
            # 这里可以添加图表交互逻辑
            print(f"点击坐标: x={x:.2f}, y={y:.2f}")
    
    def on_chart_hover(self, event):
        """图表鼠标悬停事件"""
        if event.inaxes:
            # 更新状态栏或显示详细信息
            pass
    
    def reset_chart(self):
        """重置图表"""
        self.fig.clear()
        self.canvas.draw()
        self.update_chart()
    
    def fullscreen_chart(self):
        """全屏显示图表"""
        chart_window = ChartWindow(self, "图表详情", self.fig)
        chart_window.show()
    
    def export_chart(self, format_type: str):
        """导出图表"""
        try:
            file_types = {
                'png': [('PNG文件', '*.png')],
                'pdf': [('PDF文件', '*.pdf')]
            }
            
            filename = filedialog.asksaveasfilename(
                title=f"导出图表",
                defaultextension=f".{format_type}",
                filetypes=file_types.get(format_type, [('所有文件', '*.*')])
            )
            
            if filename:
                if format_type == 'png':
                    self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                elif format_type == 'pdf':
                    self.fig.savefig(filename, bbox_inches='tight')
                
                messagebox.showinfo("成功", f"图表已导出到: {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def export_excel(self):
        """导出Excel数据"""
        try:
            filename = filedialog.asksaveasfilename(
                title="导出数据",
                defaultextension=".xlsx",
                filetypes=[('Excel文件', '*.xlsx')]
            )
            
            if filename:
                chart_type = self.current_chart_type.get()
                
                # 准备数据
                if chart_type == "sales_trend":
                    data = self.chart_manager.get_sales_data()
                    df = pd.DataFrame({
                        '日期': data['dates'],
                        '销售额': data['sales']
                    })
                elif chart_type == "product_sales":
                    data = self.chart_manager.get_product_sales_data()
                    df = pd.DataFrame({
                        '商品': data['products'],
                        '销售数量': data['sales']
                    })
                elif chart_type == "customer_analysis":
                    data = self.chart_manager.get_customer_data()
                    df = pd.DataFrame({
                        '客户类型': data['types'],
                        '客户数量': data['counts']
                    })
                elif chart_type == "inventory_analysis":
                    data = self.chart_manager.get_inventory_data()
                    df = pd.DataFrame({
                        '商品': data['products'],
                        '当前库存': data['current_stock'],
                        '最低库存': data['min_stock'],
                        '最高库存': data['max_stock']
                    })
                elif chart_type == "financial_report":
                    data = self.chart_manager.get_financial_data()
                    df = pd.DataFrame({
                        '月份': data['months'],
                        '收入': data['revenue'],
                        '支出': data['expenses'],
                        '利润': data['profit']
                    })
                
                # 导出到Excel
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='数据分析', index=False)
                
                messagebox.showinfo("成功", f"数据已导出到: {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def print_chart(self):
        """打印图表"""
        try:
            # 创建临时图像文件
            temp_file = "temp_chart.png"
            self.fig.savefig(temp_file, dpi=300, bbox_inches='tight')
            
            # 打开系统打印对话框
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(temp_file, "print")
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['lp', temp_file])
            else:  # Linux
                subprocess.run(['lpr', temp_file])
            
            messagebox.showinfo("成功", "图表已发送到打印机")
            
        except Exception as e:
            messagebox.showerror("错误", f"打印失败: {str(e)}")
    
    def toggle_auto_refresh(self):
        """切换自动刷新"""
        if self.auto_refresh_var.get():
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """开始自动刷新"""
        if not self.auto_refresh:
            self.auto_refresh = True
            self._auto_refresh_thread()
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        self.auto_refresh = False
    
    def _auto_refresh_thread(self):
        """自动刷新线程"""
        def refresh_loop():
            while self.auto_refresh:
                try:
                    interval = int(self.refresh_interval_var.get())
                    if interval > 0:
                        # 在主线程中更新图表
                        self.widget.after(0, self.update_chart)
                        time.sleep(interval)
                    else:
                        time.sleep(1)
                except:
                    time.sleep(1)
        
        if self.auto_refresh:
            thread = threading.Thread(target=refresh_loop, daemon=True)
            thread.start()


class ChartWindow:
    """图表窗口 - 用于全屏显示"""
    
    def __init__(self, parent, title: str, figure: Figure):
        self.parent = parent
        self.title = title
        self.figure = figure
        self.window = None
        
    def show(self):
        """显示窗口"""
        if not self.window:
            self.window = tk.Toplevel(self.parent.widget if hasattr(self.parent, 'widget') else self.parent)
            self.window.title(self.title)
            self.window.geometry("1000x700")
            
            # 创建工具栏
            toolbar = ttk.Frame(self.window)
            toolbar.pack(fill='x', padx=5, pady=5)
            
            ttk.Button(toolbar, text="保存", command=self.save_chart).pack(side='left', padx=5)
            ttk.Button(toolbar, text="打印", command=self.print_chart).pack(side='left', padx=5)
            ttk.Button(toolbar, text="关闭", command=self.close).pack(side='right', padx=5)
            
            # 创建画布
            canvas = FigureCanvasTkAgg(self.figure, self.window)
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
            
            # 绑定事件
            self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def save_chart(self):
        """保存图表"""
        try:
            filename = filedialog.asksaveasfilename(
                title="保存图表",
                defaultextension=".png",
                filetypes=[('PNG文件', '*.png'), ('PDF文件', '*.pdf')]
            )
            
            if filename:
                if filename.endswith('.png'):
                    self.figure.savefig(filename, dpi=300, bbox_inches='tight')
                else:
                    self.figure.savefig(filename, bbox_inches='tight')
                messagebox.showinfo("成功", f"图表已保存到: {filename}")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def print_chart(self):
        """打印图表"""
        try:
            temp_file = "temp_chart_fullscreen.png"
            self.figure.savefig(temp_file, dpi=300, bbox_inches='tight')
            
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(temp_file, "print")
            elif platform.system() == 'Darwin':
                subprocess.run(['lp', temp_file])
            else:
                subprocess.run(['lpr', temp_file])
            
            messagebox.showinfo("成功", "图表已发送到打印机")
            
        except Exception as e:
            messagebox.showerror("错误", f"打印失败: {str(e)}")
    
    def close(self):
        """关闭窗口"""
        if self.window:
            self.window.destroy()
            self.window = None


class DataAnalyticsPanel(BaseFrame):
    """数据分析面板"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.chart_manager = ChartManager()
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_label = ttk.Label(self.widget, text="数据分析中心", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # 快捷操作
        quick_frame = ttk.LabelFrame(self.widget, text="快捷操作", padding=10)
        quick_frame.pack(fill='x', padx=20, pady=10)
        
        buttons = [
            ("销售分析", lambda: self.show_chart("sales_trend")),
            ("商品分析", lambda: self.show_chart("product_sales")),
            ("客户分析", lambda: self.show_chart("customer_analysis")),
            ("库存分析", lambda: self.show_chart("inventory_analysis")),
            ("财务分析", lambda: self.show_chart("financial_report"))
        ]
        
        for i, (text, command) in enumerate(buttons):
            row = i // 3
            col = i % 3
            ttk.Button(quick_frame, text=text, command=command, 
                      width=15).grid(row=row, column=col, padx=5, pady=5)
        
        # 数据显示区域
        self.data_frame = ttk.Frame(self.widget)
        self.data_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 实时数据更新
        self.update_realtime_data()
        
    def show_chart(self, chart_type: str):
        """显示图表"""
        # 创建新窗口显示图表
        window = tk.Toplevel(self.widget)
        window.title("数据分析图表")
        window.geometry("1200x800")
        
        analytics_gui = AnalyticsChartsGUI(window)
        analytics_gui.current_chart_type.set(chart_type)
        analytics_gui.update_chart()
        analytics_gui.pack(fill='both', expand=True)
        
    def update_realtime_data(self):
        """更新实时数据"""
        try:
            # 清除旧数据
            for widget in self.data_frame.winfo_children():
                widget.destroy()
            
            # 获取数据
            sales_data = self.chart_manager.get_sales_data(7)
            inventory_data = self.chart_manager.get_inventory_data()
            customer_data = self.chart_manager.get_customer_data()
            
            # 今日销售
            today_frame = ttk.LabelFrame(self.data_frame, text="今日销售概况", padding=10)
            today_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
            
            today_sales = sales_data['sales'][-1] if sales_data['sales'] else 0
            ttk.Label(today_frame, text=f"今日销售额: {today_sales:,.0f} 元", 
                     font=('Arial', 12, 'bold')).pack()
            ttk.Label(today_frame, text=f"7日总销售额: {sum(sales_data['sales']):,.0f} 元").pack()
            
            # 库存预警
            inventory_frame = ttk.LabelFrame(self.data_frame, text="库存预警", padding=10)
            inventory_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            if len(inventory_data['low_stock_items']) > 0:
                for item in inventory_data['low_stock_items'][:5]:  # 显示前5个
                    ttk.Label(inventory_frame, text=f"⚠️ {item}", 
                             foreground="red").pack(anchor='w')
            else:
                ttk.Label(inventory_frame, text="✅ 所有商品库存正常").pack()
            
            # 客户统计
            customer_frame = ttk.LabelFrame(self.data_frame, text="客户统计", padding=10)
            customer_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
            
            ttk.Label(customer_frame, text=f"总客户数: {customer_data['total']} 人").pack()
            ttk.Label(customer_frame, text=f"新增客户: {customer_data['counts'][0]} 人").pack()
            
        except Exception as e:
            print(f"更新实时数据失败: {e}")
        
        # 5秒后再次更新
        if hasattr(self, 'widget') and self.widget:
            try:
                self.widget.after(5000, self.update_realtime_data)
            except:
                pass  # 如果widget不存在则跳过


def create_analytics_demo():
    """创建数据分析演示"""
    root = tk.Tk()
    root.title("数据分析图表系统演示")
    root.geometry("1200x800")
    
    # 创建主界面
    analytics_panel = DataAnalyticsPanel(root)
    analytics_panel.pack(fill='both', expand=True)
    
    # 添加菜单栏
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # 文件菜单
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="文件", menu=file_menu)
    file_menu.add_command(label="新建分析", command=lambda: analytics_panel.show_chart("sales_trend"))
    file_menu.add_separator()
    file_menu.add_command(label="退出", command=root.quit)
    
    # 分析菜单
    analysis_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="分析", menu=analysis_menu)
    analysis_menu.add_command(label="销售分析", command=lambda: analytics_panel.show_chart("sales_trend"))
    analysis_menu.add_command(label="商品分析", command=lambda: analytics_panel.show_chart("product_sales"))
    analysis_menu.add_command(label="客户分析", command=lambda: analytics_panel.show_chart("customer_analysis"))
    analysis_menu.add_command(label="库存分析", command=lambda: analytics_panel.show_chart("inventory_analysis"))
    analysis_menu.add_command(label="财务分析", command=lambda: analytics_panel.show_chart("financial_report"))
    
    # 帮助菜单
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="帮助", menu=help_menu)
    help_menu.add_command(label="关于", command=lambda: messagebox.showinfo("关于", "数据分析图表系统 v1.0"))
    
    return root


if __name__ == "__main__":
    # 运行演示
    demo = create_analytics_demo()
    demo.mainloop()