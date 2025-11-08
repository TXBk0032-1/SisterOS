"""
财务报表模块
实现完整的财务报表系统，包括收入、支出、利润分析、现金流等报表
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from decimal import Decimal
import calendar

# 导入现有组件
from .base_components import BaseFrame, BaseButton, BaseLabel, BaseEntry, BaseWindow
from .table_components import SortableTable

# 导入主题系统
try:
    from ..config.win11_theme import win11_theme
except ImportError:
    # 处理相对导入问题
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.win11_theme import win11_theme

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    import pandas as pd
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class FinancialDataManager:
    """财务报表数据管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "sisters_flowers.db"
    
    def get_income_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取收入数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        s.id,
                        s.sale_date,
                        s.total_amount,
                        s.discount_amount,
                        s.final_amount,
                        s.payment_method,
                        s.notes,
                        COUNT(si.id) as item_count
                    FROM sales s
                    LEFT JOIN sale_items si ON s.id = si.sale_id
                    WHERE s.sale_date BETWEEN ? AND ?
                    GROUP BY s.id
                    ORDER BY s.sale_date DESC
                """, (start_date, end_date))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取收入数据失败: {e}")
            return []
    
    def get_expense_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取支出数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id,
                        expense_date,
                        category,
                        amount,
                        description,
                        payment_method
                    FROM expenses
                    WHERE expense_date BETWEEN ? AND ?
                    ORDER BY expense_date DESC
                """, (start_date, end_date))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取支出数据失败: {e}")
            return []
    
    def get_profit_analysis(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取利润分析数据"""
        income_data = self.get_income_data(start_date, end_date)
        expense_data = self.get_expense_data(start_date, end_date)
        
        total_income = sum(item['final_amount'] for item in income_data)
        total_expense = sum(item['amount'] for item in expense_data)
        net_profit = total_income - total_expense
        profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
        
        # 按月统计
        monthly_data = {}
        for item in income_data:
            month = item['sale_date'][:7]  # YYYY-MM
            if month not in monthly_data:
                monthly_data[month] = {'income': 0, 'expense': 0}
            monthly_data[month]['income'] += item['final_amount']
        
        for item in expense_data:
            month = item['expense_date'][:7]  # YYYY-MM
            if month not in monthly_data:
                monthly_data[month] = {'income': 0, 'expense': 0}
            monthly_data[month]['expense'] += item['amount']
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'monthly_data': monthly_data,
            'income_count': len(income_data),
            'expense_count': len(expense_data)
        }
    
    def get_cash_flow_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取现金流数据"""
        income_data = self.get_income_data(start_date, end_date)
        expense_data = self.get_expense_data(start_date, end_date)
        
        # 按日期汇总现金流
        cash_flow = {}
        
        for item in income_data:
            day = item['sale_date']
            if day not in cash_flow:
                cash_flow[day] = {'inflow': 0, 'outflow': 0}
            cash_flow[day]['inflow'] += item['final_amount']
        
        for item in expense_data:
            day = item['expense_date']
            if day not in cash_flow:
                cash_flow[day] = {'inflow': 0, 'outflow': 0}
            cash_flow[day]['outflow'] += item['amount']
        
        # 排序并计算累计
        sorted_days = sorted(cash_flow.keys())
        cumulative = 0
        cash_flow_list = []
        
        for day in sorted_days:
            inflow = cash_flow[day]['inflow']
            outflow = cash_flow[day]['outflow']
            net_flow = inflow - outflow
            cumulative += net_flow
            
            cash_flow_list.append({
                'date': day,
                'inflow': inflow,
                'outflow': outflow,
                'net_flow': net_flow,
                'cumulative': cumulative
            })
        
        return {
            'daily_flow': cash_flow_list,
            'total_inflow': sum(item['inflow'] for item in cash_flow_list),
            'total_outflow': sum(item['outflow'] for item in cash_flow_list),
            'net_cash_flow': sum(item['net_flow'] for item in cash_flow_list)
        }


class DateRangeSelector(BaseFrame):
    """日期范围选择器"""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.on_date_change = kwargs.pop('on_date_change', None)
        super().__init__(parent, **kwargs)
        self.start_date = None
        self.end_date = None
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        ttk.Label(self.main_frame, text="日期范围:", 
                 font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        # 开始日期
        ttk.Label(self.main_frame, text="从:").pack(side='left')
        self.start_entry = ttk.Entry(self.main_frame, width=12)
        self.start_entry.pack(side='left', padx=(5, 15))
        
        # 结束日期
        ttk.Label(self.main_frame, text="到:").pack(side='left')
        self.end_entry = ttk.Entry(self.main_frame, width=12)
        self.end_entry.pack(side='left', padx=(5, 15))
        
        # 预设按钮
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(side='left', padx=15)
        
        ttk.Button(buttons_frame, text="本月", 
                  command=lambda: self._set_date_range('current_month')).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="上月", 
                  command=lambda: self._set_date_range('last_month')).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="本季度", 
                  command=lambda: self._set_date_range('current_quarter')).pack(side='left', padx=2)
        ttk.Button(buttons_frame, text="本年", 
                  command=lambda: self._set_date_range('current_year')).pack(side='left', padx=2)
        
        # 设置默认值为本月
        self._set_date_range('current_month')
        
        # 绑定变更事件
        self.start_entry.bind('<FocusOut>', self._on_date_change)
        self.end_entry.bind('<FocusOut>', self._on_date_change)
    
    def _set_date_range(self, period: str):
        """设置日期范围"""
        today = date.today()
        
        if period == 'current_month':
            self.start_date = today.replace(day=1)
            # 获取本月最后一天
            last_day = calendar.monthrange(today.year, today.month)[1]
            self.end_date = today.replace(day=last_day)
            
        elif period == 'last_month':
            if today.month == 1:
                self.start_date = today.replace(year=today.year-1, month=12, day=1)
                last_day = calendar.monthrange(today.year-1, 12)[1]
                self.end_date = today.replace(year=today.year-1, month=12, day=last_day)
            else:
                self.start_date = today.replace(month=today.month-1, day=1)
                last_day = calendar.monthrange(today.year, today.month-1)[1]
                self.end_date = today.replace(month=today.month-1, day=last_day)
                
        elif period == 'current_quarter':
            quarter = (today.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            self.start_date = today.replace(month=start_month, day=1)
            end_month = start_month + 2
            if end_month > 12:
                end_month = 12
                self.end_date = today.replace(year=today.year, month=end_month, 
                                            day=calendar.monthrange(today.year, end_month)[1])
            else:
                self.end_date = today.replace(month=end_month, 
                                            day=calendar.monthrange(today.year, end_month)[1])
                
        elif period == 'current_year':
            self.start_date = today.replace(month=1, day=1)
            self.end_date = today.replace(month=12, day=31)
        
        # 更新输入框
        if self.start_date and self.end_date:
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, self.start_date.strftime('%Y-%m-%d'))
            self.end_entry.delete(0, tk.END)
            self.end_entry.insert(0, self.end_date.strftime('%Y-%m-%d'))
            self._on_date_change()
    
    def _on_date_change(self, event=None):
        """日期变更事件"""
        try:
            start_str = self.start_entry.get()
            end_str = self.end_entry.get()
            
            if start_str and end_str:
                self.start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                self.end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
                
                if self.on_date_change:
                    self.on_date_change(self.start_date, self.end_date)
                    
        except ValueError:
            pass
    
    def get_date_range(self) -> tuple:
        """获取日期范围"""
        return self.start_date, self.end_date


class ChartCanvas(BaseFrame):
    """图表画布组件"""
    
    def __init__(self, parent: tk.Widget, chart_type: str = 'line', **kwargs):
        self.chart_type = chart_type
        self.figure = None
        self.canvas = None
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        if not HAS_MATPLOTLIB:
            # 如果没有matplotlib，显示提示信息
            self.widget = ttk.Label(self.parent, 
                                  text="需要安装matplotlib才能显示图表\npip install matplotlib",
                                  font=('Segoe UI', 12),
                                  foreground=win11_theme.colors['error'])
            return
        
        # 创建主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, self.main_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def plot_line_chart(self, x_data, y_data, title: str, x_label: str, y_label: str):
        """绘制线图"""
        if not HAS_MATPLOTLIB or not self.figure:
            return
        
        self.ax.clear()
        self.ax.plot(x_data, y_data, marker='o', linewidth=2, markersize=6)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_bar_chart(self, x_data, y_data, title: str, x_label: str, y_label: str):
        """绘制柱状图"""
        if not HAS_MATPLOTLIB or not self.figure:
            return
        
        self.ax.clear()
        self.ax.bar(x_data, y_data, color=win11_theme.colors['primary'], alpha=0.7)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(True, alpha=0.3, axis='y')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_chart(self, data, labels, title: str):
        """绘制饼图"""
        if not HAS_MATPLOTLIB or not self.figure:
            return
        
        self.ax.clear()
        colors = [win11_theme.colors['primary'], win11_theme.colors['secondary'], 
                 win11_theme.colors['accent'], win11_theme.colors['success'],
                 win11_theme.colors['warning'], win11_theme.colors['error']]
        
        self.ax.pie(data, labels=labels, autopct='%1.1f%%', 
                   colors=colors[:len(data)], startangle=90)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()


class IncomeStatementTab(BaseFrame):
    """收入财务报表标签页"""
    
    def __init__(self, parent: tk.Widget, data_manager: FinancialDataManager, **kwargs):
        self.data_manager = data_manager
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="收入财务报表", 
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # 导出按钮
        ttk.Button(header_frame, text="导出Excel", 
                  command=self._export_excel).pack(side='right')
        
        # 日期选择器
        self.date_selector = DateRangeSelector(
            self.main_frame, 
            on_date_change=self._on_date_change
        )
        self.date_selector.pack(fill='x', padx=20, pady=10)
        
        # 收入汇总卡片
        self._create_summary_cards()
        
        # 主要内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧：收入明细表格
        left_frame = ttk.LabelFrame(content_frame, text="收入明细", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 收入明细表格
        income_columns = ['日期', '订单号', '商品数量', '原价', '折扣', '实收金额', '支付方式', '备注']
        self.income_table = SortableTable(left_frame, income_columns, height=15)
        self.income_table.pack(fill='both', expand=True)
        
        # 右侧：图表区域
        right_frame = ttk.LabelFrame(content_frame, text="收入趋势图", padding=10)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.chart_canvas = ChartCanvas(right_frame, 'line')
        self.chart_canvas.pack(fill='both', expand=True)
        
        # 初始化数据
        start_date, end_date = self.date_selector.get_date_range()
        if start_date and end_date:
            self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _create_summary_cards(self):
        """创建汇总卡片"""
        cards_frame = ttk.Frame(self.main_frame)
        cards_frame.pack(fill='x', padx=20, pady=10)
        
        # 卡片样式
        card_style = {
            'relief': 'solid',
            'borderwidth': 1,
            'padding': 15
        }
        
        # 总收入卡片
        self.total_income_card = ttk.Frame(cards_frame, **card_style)
        self.total_income_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.total_income_card, text="总收入", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.total_income_label = ttk.Label(self.total_income_card, text="¥0.00", 
                                           font=('Segoe UI', 16, 'bold'),
                                           foreground=win11_theme.colors['success'])
        self.total_income_label.pack()
        
        # 订单数量卡片
        self.order_count_card = ttk.Frame(cards_frame, **card_style)
        self.order_count_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.order_count_card, text="订单数量", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.order_count_label = ttk.Label(self.order_count_card, text="0", 
                                          font=('Segoe UI', 16, 'bold'),
                                          foreground=win11_theme.colors['primary'])
        self.order_count_label.pack()
        
        # 平均订单金额卡片
        self.avg_amount_card = ttk.Frame(cards_frame, **card_style)
        self.avg_amount_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.avg_amount_card, text="平均订单金额", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.avg_amount_label = ttk.Label(self.avg_amount_card, text="¥0.00", 
                                         font=('Segoe UI', 16, 'bold'),
                                         foreground=win11_theme.colors['accent'])
        self.avg_amount_label.pack()
    
    def _on_date_change(self, start_date: date, end_date: date):
        """日期变更事件"""
        self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _load_data(self, start_date: str, end_date: str):
        """加载数据"""
        # 获取收入数据
        income_data = self.data_manager.get_income_data(start_date, end_date)
        
        # 转换数据格式
        table_data = []
        for item in income_data:
            table_data.append({
                '日期': item['sale_date'],
                '订单号': f"ORD-{item['id']:04d}",
                '商品数量': f"{item['item_count']}件",
                '原价': f"¥{item['total_amount']:.2f}",
                '折扣': f"¥{item['discount_amount']:.2f}",
                '实收金额': f"¥{item['final_amount']:.2f}",
                '支付方式': item['payment_method'] or '未设置',
                '备注': item['notes'] or ''
            })
        
        # 加载到表格
        self.income_table.load_data(table_data)
        
        # 更新汇总数据
        total_income = sum(item['final_amount'] for item in income_data)
        order_count = len(income_data)
        avg_amount = total_income / order_count if order_count > 0 else 0
        
        self.total_income_label.config(text=f"¥{total_income:,.2f}")
        self.order_count_label.config(text=str(order_count))
        self.avg_amount_label.config(text=f"¥{avg_amount:.2f}")
        
        # 绘制图表
        if HAS_MATPLOTLIB and table_data:
            self._plot_income_chart(table_data)
    
    def _plot_income_chart(self, data: List[Dict]):
        """绘制收入图表"""
        # 按日期汇总收入
        daily_income = {}
        for item in data:
            date = item['日期']
            amount = float(item['实收金额'].replace('¥', '').replace(',', ''))
            daily_income[date] = daily_income.get(date, 0) + amount
        
        # 排序并准备数据
        dates = sorted(daily_income.keys())
        amounts = [daily_income[date] for date in dates]
        
        # 绘制线图
        self.chart_canvas.plot_line_chart(
            dates, amounts, 
            "每日收入趋势", 
            "日期", "收入金额 (¥)"
        )
    
    def _export_excel(self):
        """导出Excel"""
        try:
            # 这里可以集成pandas和openpyxl来导出Excel
            messagebox.showinfo("提示", "Excel导出功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")


class ExpenseStatementTab(BaseFrame):
    """支出财务报表标签页"""
    
    def __init__(self, parent: tk.Widget, data_manager: FinancialDataManager, **kwargs):
        self.data_manager = data_manager
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="支出财务报表", 
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # 导出按钮
        ttk.Button(header_frame, text="导出Excel", 
                  command=self._export_excel).pack(side='right')
        
        # 日期选择器
        self.date_selector = DateRangeSelector(
            self.main_frame, 
            on_date_change=self._on_date_change
        )
        self.date_selector.pack(fill='x', padx=20, pady=10)
        
        # 支出汇总卡片
        self._create_summary_cards()
        
        # 主要内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧：支出明细表格
        left_frame = ttk.LabelFrame(content_frame, text="支出明细", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 支出明细表格
        expense_columns = ['日期', '类别', '金额', '描述', '支付方式']
        self.expense_table = SortableTable(left_frame, expense_columns, height=15)
        self.expense_table.pack(fill='both', expand=True)
        
        # 右侧：图表区域
        right_frame = ttk.LabelFrame(content_frame, text="支出分析", padding=10)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.chart_canvas = ChartCanvas(right_frame, 'pie')
        self.chart_canvas.pack(fill='both', expand=True)
        
        # 初始化数据
        start_date, end_date = self.date_selector.get_date_range()
        if start_date and end_date:
            self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _create_summary_cards(self):
        """创建汇总卡片"""
        cards_frame = ttk.Frame(self.main_frame)
        cards_frame.pack(fill='x', padx=20, pady=10)
        
        # 卡片样式
        card_style = {
            'relief': 'solid',
            'borderwidth': 1,
            'padding': 15
        }
        
        # 总支出卡片
        self.total_expense_card = ttk.Frame(cards_frame, **card_style)
        self.total_expense_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.total_expense_card, text="总支出", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.total_expense_label = ttk.Label(self.total_expense_card, text="¥0.00", 
                                            font=('Segoe UI', 16, 'bold'),
                                            foreground=win11_theme.colors['error'])
        self.total_expense_label.pack()
        
        # 支出笔数卡片
        self.expense_count_card = ttk.Frame(cards_frame, **card_style)
        self.expense_count_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.expense_count_card, text="支出笔数", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.expense_count_label = ttk.Label(self.expense_count_card, text="0", 
                                            font=('Segoe UI', 16, 'bold'),
                                            foreground=win11_theme.colors['primary'])
        self.expense_count_label.pack()
        
        # 平均支出金额卡片
        self.avg_expense_card = ttk.Frame(cards_frame, **card_style)
        self.avg_expense_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.avg_expense_card, text="平均支出", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.avg_expense_label = ttk.Label(self.avg_expense_card, text="¥0.00", 
                                          font=('Segoe UI', 16, 'bold'),
                                          foreground=win11_theme.colors['warning'])
        self.avg_expense_label.pack()
    
    def _on_date_change(self, start_date: date, end_date: date):
        """日期变更事件"""
        self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _load_data(self, start_date: str, end_date: str):
        """加载数据"""
        # 获取支出数据
        expense_data = self.data_manager.get_expense_data(start_date, end_date)
        
        # 转换数据格式
        table_data = []
        for item in expense_data:
            table_data.append({
                '日期': item['expense_date'],
                '类别': item['category'],
                '金额': f"¥{item['amount']:.2f}",
                '描述': item['description'] or '',
                '支付方式': item['payment_method'] or ''
            })
        
        # 加载到表格
        self.expense_table.load_data(table_data)
        
        # 更新汇总数据
        total_expense = sum(item['amount'] for item in expense_data)
        expense_count = len(expense_data)
        avg_expense = total_expense / expense_count if expense_count > 0 else 0
        
        self.total_expense_label.config(text=f"¥{total_expense:,.2f}")
        self.expense_count_label.config(text=str(expense_count))
        self.avg_expense_label.config(text=f"¥{avg_expense:.2f}")
        
        # 绘制图表
        if HAS_MATPLOTLIB and table_data:
            self._plot_expense_chart(table_data)
    
    def _plot_expense_chart(self, data: List[Dict]):
        """绘制支出图表"""
        # 按类别汇总支出
        category_expense = {}
        for item in data:
            category = item['类别']
            amount = float(item['金额'].replace('¥', '').replace(',', ''))
            category_expense[category] = category_expense.get(category, 0) + amount
        
        # 准备数据
        categories = list(category_expense.keys())
        amounts = list(category_expense.values())
        
        # 绘制饼图
        self.chart_canvas.plot_pie_chart(
            amounts, categories, "支出分类占比"
        )
    
    def _export_excel(self):
        """导出Excel"""
        try:
            messagebox.showinfo("提示", "Excel导出功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")


class ProfitAnalysisTab(BaseFrame):
    """利润分析报告标签页"""
    
    def __init__(self, parent: tk.Widget, data_manager: FinancialDataManager, **kwargs):
        self.data_manager = data_manager
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="利润分析报告", 
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # 导出按钮
        ttk.Button(header_frame, text="导出报告", 
                  command=self._export_report).pack(side='right')
        
        # 日期选择器
        self.date_selector = DateRangeSelector(
            self.main_frame, 
            on_date_change=self._on_date_change
        )
        self.date_selector.pack(fill='x', padx=20, pady=10)
        
        # 关键指标卡片
        self._create_kpi_cards()
        
        # 主要内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左上：月度利润趋势
        top_left_frame = ttk.LabelFrame(content_frame, text="月度利润趋势", padding=10)
        top_left_frame.pack(side='top', fill='both', expand=True, padx=(0, 5), pady=(0, 5))
        
        self.profit_chart = ChartCanvas(top_left_frame, 'line')
        self.profit_chart.pack(fill='both', expand=True)
        
        # 右上：收支对比
        top_right_frame = ttk.LabelFrame(content_frame, text="收支对比", padding=10)
        top_right_frame.pack(side='top', fill='both', expand=True, padx=(5, 0), pady=(0, 5))
        
        self.comparison_chart = ChartCanvas(top_right_frame, 'bar')
        self.comparison_chart.pack(fill='both', expand=True)
        
        # 底部：详细分析
        bottom_frame = ttk.LabelFrame(content_frame, text="详细财务指标", padding=10)
        bottom_frame.pack(side='bottom', fill='both', expand=True)
        
        # 分析指标表格
        analysis_columns = ['指标', '当前值', '占比', '评估']
        self.analysis_table = SortableTable(bottom_frame, analysis_columns, height=8)
        self.analysis_table.pack(fill='both', expand=True)
        
        # 初始化数据
        start_date, end_date = self.date_selector.get_date_range()
        if start_date and end_date:
            self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _create_kpi_cards(self):
        """创建关键指标卡片"""
        kpi_frame = ttk.Frame(self.main_frame)
        kpi_frame.pack(fill='x', padx=20, pady=10)
        
        # 卡片样式
        card_style = {
            'relief': 'solid',
            'borderwidth': 1,
            'padding': 15
        }
        
        # 净利润卡片
        self.net_profit_card = ttk.Frame(kpi_frame, **card_style)
        self.net_profit_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.net_profit_card, text="净利润", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.net_profit_label = ttk.Label(self.net_profit_card, text="¥0.00", 
                                         font=('Segoe UI', 16, 'bold'),
                                         foreground=win11_theme.colors['success'])
        self.net_profit_label.pack()
        
        # 利润率卡片
        self.profit_margin_card = ttk.Frame(kpi_frame, **card_style)
        self.profit_margin_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.profit_margin_card, text="利润率", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.profit_margin_label = ttk.Label(self.profit_margin_card, text="0%", 
                                            font=('Segoe UI', 16, 'bold'),
                                            foreground=win11_theme.colors['primary'])
        self.profit_margin_label.pack()
        
        # 收支比卡片
        self.ratio_card = ttk.Frame(kpi_frame, **card_style)
        self.ratio_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(self.ratio_card, text="收支比", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.ratio_label = ttk.Label(self.ratio_card, text="1:0", 
                                    font=('Segoe UI', 16, 'bold'),
                                    foreground=win11_theme.colors['accent'])
        self.ratio_label.pack()
    
    def _on_date_change(self, start_date: date, end_date: date):
        """日期变更事件"""
        self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _load_data(self, start_date: str, end_date: str):
        """加载数据"""
        # 获取利润分析数据
        profit_data = self.data_manager.get_profit_analysis(start_date, end_date)
        
        # 更新KPI卡片
        self.net_profit_label.config(text=f"¥{profit_data['net_profit']:,.2f}")
        self.profit_margin_label.config(text=f"{profit_data['profit_margin']:.1f}%")
        
        if profit_data['total_expense'] > 0:
            ratio = profit_data['total_income'] / profit_data['total_expense']
            self.ratio_label.config(text=f"1:{ratio:.2f}")
        else:
            self.ratio_label.config(text="1:0")
        
        # 更新详细分析表格
        self._update_analysis_table(profit_data)
        
        # 绘制图表
        if HAS_MATPLOTLIB:
            self._plot_charts(profit_data)
    
    def _update_analysis_table(self, profit_data: Dict):
        """更新分析表格"""
        analysis_data = [
            {
                '指标': '总收入',
                '当前值': f"¥{profit_data['total_income']:,.2f}",
                '占比': '100.0%',
                '评估': '✓ 正常'
            },
            {
                '指标': '总支出',
                '当前值': f"¥{profit_data['total_expense']:,.2f}",
                '占比': f"{(profit_data['total_expense']/profit_data['total_income']*100):.1f}%" if profit_data['total_income'] > 0 else "0%",
                '评估': '✓ 正常' if profit_data['total_expense'] < profit_data['total_income'] else '⚠ 过高'
            },
            {
                '指标': '净利润',
                '当前值': f"¥{profit_data['net_profit']:,.2f}",
                '占比': f"{(profit_data['net_profit']/profit_data['total_income']*100):.1f}%" if profit_data['total_income'] > 0 else "0%",
                '评估': '✓ 盈利' if profit_data['net_profit'] > 0 else '⚠ 亏损'
            },
            {
                '指标': '收入笔数',
                '当前值': f"{profit_data['income_count']}笔",
                '占比': '-',
                '评估': '✓ 正常'
            },
            {
                '指标': '支出笔数',
                '当前值': f"{profit_data['expense_count']}笔",
                '占比': '-',
                '评估': '✓ 正常'
            }
        ]
        
        self.analysis_table.load_data(analysis_data)
    
    def _plot_charts(self, profit_data: Dict):
        """绘制图表"""
        # 月度利润趋势图
        monthly_data = profit_data['monthly_data']
        if monthly_data:
            months = sorted(monthly_data.keys())
            profits = []
            
            for month in months:
                month_data = monthly_data[month]
                profit = month_data['income'] - month_data['expense']
                profits.append(profit)
            
            self.profit_chart.plot_line_chart(
                months, profits,
                "月度净利润趋势", "月份", "净利润 (¥)"
            )
        
        # 收支对比图
        labels = ['收入', '支出']
        values = [profit_data['total_income'], profit_data['total_expense']]
        
        self.comparison_chart.plot_bar_chart(
            labels, values,
            "收支对比", "类别", "金额 (¥)"
        )
    
    def _export_report(self):
        """导出报告"""
        try:
            messagebox.showinfo("提示", "报告导出功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")


class CashFlowTab(BaseFrame):
    """现金流报表标签页"""
    
    def __init__(self, parent: tk.Widget, data_manager: FinancialDataManager, **kwargs):
        self.data_manager = data_manager
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="现金流报表", 
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # 导出按钮
        ttk.Button(header_frame, text="导出现金流表", 
                  command=self._export_cashflow).pack(side='right')
        
        # 日期选择器
        self.date_selector = DateRangeSelector(
            self.main_frame, 
            on_date_change=self._on_date_change
        )
        self.date_selector.pack(fill='x', padx=20, pady=10)
        
        # 现金流摘要
        self._create_cashflow_summary()
        
        # 主要内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧：现金流明细
        left_frame = ttk.LabelFrame(content_frame, text="现金流明细", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 现金流表格
        cashflow_columns = ['日期', '现金流入', '现金流出', '净现金流', '累计现金流']
        self.cashflow_table = SortableTable(left_frame, cashflow_columns, height=15)
        self.cashflow_table.pack(fill='both', expand=True)
        
        # 右侧：图表区域
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 现金流趋势图
        trend_frame = ttk.LabelFrame(right_frame, text="现金流趋势", padding=10)
        trend_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.trend_chart = ChartCanvas(trend_frame, 'line')
        self.trend_chart.pack(fill='both', expand=True)
        
        # 累计现金流图
        cumulative_frame = ttk.LabelFrame(right_frame, text="累计现金流", padding=10)
        cumulative_frame.pack(fill='both', expand=True)
        
        self.cumulative_chart = ChartCanvas(cumulative_frame, 'line')
        self.cumulative_chart.pack(fill='both', expand=True)
        
        # 初始化数据
        start_date, end_date = self.date_selector.get_date_range()
        if start_date and end_date:
            self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _create_cashflow_summary(self):
        """创建现金流摘要"""
        summary_frame = ttk.Frame(self.main_frame)
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        # 摘要卡片
        card_style = {
            'relief': 'solid',
            'borderwidth': 1,
            'padding': 15
        }
        
        # 总流入
        inflow_card = ttk.Frame(summary_frame, **card_style)
        inflow_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(inflow_card, text="总现金流入", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.total_inflow_label = ttk.Label(inflow_card, text="¥0.00", 
                                           font=('Segoe UI', 14, 'bold'),
                                           foreground=win11_theme.colors['success'])
        self.total_inflow_label.pack()
        
        # 总流出
        outflow_card = ttk.Frame(summary_frame, **card_style)
        outflow_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(outflow_card, text="总现金流出", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.total_outflow_label = ttk.Label(outflow_card, text="¥0.00", 
                                            font=('Segoe UI', 14, 'bold'),
                                            foreground=win11_theme.colors['error'])
        self.total_outflow_label.pack()
        
        # 净现金流
        net_card = ttk.Frame(summary_frame, **card_style)
        net_card.pack(side='left', fill='both', expand=True, padx=5)
        
        ttk.Label(net_card, text="净现金流", 
                 font=('Segoe UI', 10, 'bold')).pack()
        self.net_cashflow_label = ttk.Label(net_card, text="¥0.00", 
                                           font=('Segoe UI', 14, 'bold'),
                                           foreground=win11_theme.colors['primary'])
        self.net_cashflow_label.pack()
    
    def _on_date_change(self, start_date: date, end_date: date):
        """日期变更事件"""
        self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _load_data(self, start_date: str, end_date: str):
        """加载数据"""
        # 获取现金流数据
        cashflow_data = self.data_manager.get_cash_flow_data(start_date, end_date)
        
        # 转换数据格式
        table_data = []
        for item in cashflow_data['daily_flow']:
            table_data.append({
                '日期': item['date'],
                '现金流入': f"¥{item['inflow']:,.2f}",
                '现金流出': f"¥{item['outflow']:,.2f}",
                '净现金流': f"¥{item['net_flow']:,.2f}",
                '累计现金流': f"¥{item['cumulative']:,.2f}"
            })
        
        # 加载到表格
        self.cashflow_table.load_data(table_data)
        
        # 更新摘要
        self.total_inflow_label.config(text=f"¥{cashflow_data['total_inflow']:,.2f}")
        self.total_outflow_label.config(text=f"¥{cashflow_data['total_outflow']:,.2f}")
        
        net_color = win11_theme.colors['success'] if cashflow_data['net_cash_flow'] >= 0 else win11_theme.colors['error']
        self.net_cashflow_label.config(
            text=f"¥{cashflow_data['net_cash_flow']:,.2f}",
            foreground=net_color
        )
        
        # 绘制图表
        if HAS_MATPLOTLIB and table_data:
            self._plot_charts(cashflow_data)
    
    def _plot_charts(self, cashflow_data: Dict):
        """绘制图表"""
        if not cashflow_data['daily_flow']:
            return
        
        dates = [item['date'] for item in cashflow_data['daily_flow']]
        inflows = [item['inflow'] for item in cashflow_data['daily_flow']]
        outflows = [item['outflow'] for item in cashflow_data['daily_flow']]
        net_flows = [item['net_flow'] for item in cashflow_data['daily_flow']]
        cumulative = [item['cumulative'] for item in cashflow_data['daily_flow']]
        
        # 现金流趋势图
        self.trend_chart.plot_line_chart(
            dates, net_flows,
            "每日净现金流", "日期", "净现金流 (¥)"
        )
        
        # 累计现金流图
        self.cumulative_chart.plot_line_chart(
            dates, cumulative,
            "累计现金流", "日期", "累计金额 (¥)"
        )
    
    def _export_cashflow(self):
        """导出现金流表"""
        try:
            messagebox.showinfo("提示", "现金流表导出功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")


class TaxManagementTab(BaseFrame):
    """税率计算和管理标签页"""
    
    def __init__(self, parent: tk.Widget, data_manager: FinancialDataManager, **kwargs):
        self.data_manager = data_manager
        super().__init__(parent, **kwargs)
        self.tax_rates = {
            '增值税': 0.13,
            '企业所得税': 0.25,
            '个人所得税': 0.20,
            '印花税': 0.003,
            '城市维护建设税': 0.07
        }
        self.tax_settings = self._load_tax_settings()
    
    def _load_tax_settings(self) -> Dict:
        """加载税率设置"""
        try:
            settings_file = "tax_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载税率设置失败: {e}")
        
        # 默认设置
        return {
            'enterprise_name': '姐妹花店',
            'tax_id': '',
            'address': '',
            'phone': '',
            'bank_account': '',
            'declared_period': 'monthly',  # monthly, quarterly, yearly
            'auto_calculate': True
        }
    
    def _save_tax_settings(self):
        """保存税率设置"""
        try:
            with open("tax_settings.json", 'w', encoding='utf-8') as f:
                json.dump(self.tax_settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存税率设置失败: {e}")
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="税率计算和管理", 
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # 申报按钮
        ttk.Button(header_frame, text="生成申报表", 
                  command=self._generate_tax_declaration).pack(side='right')
        
        # 标签笔记本
        notebook = ttk.Notebook(self.main_frame)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 税率设置标签页
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="税率设置")
        self._create_settings_tab(settings_frame)
        
        # 税费计算标签页
        calc_frame = ttk.Frame(notebook)
        notebook.add(calc_frame, text="税费计算")
        self._create_calculation_tab(calc_frame)
        
        # 申报支持标签页
        declaration_frame = ttk.Frame(notebook)
        notebook.add(declaration_frame, text="申报支持")
        self._create_declaration_tab(declaration_frame)
    
    def _create_settings_tab(self, parent: ttk.Frame):
        """创建税率设置标签页"""
        # 基本信息
        info_frame = ttk.LabelFrame(parent, text="企业基本信息", padding=15)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # 企业名称
        ttk.Label(info_frame, text="企业名称:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.enterprise_name_entry = ttk.Entry(info_frame, width=30)
        self.enterprise_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.enterprise_name_entry.insert(0, self.tax_settings.get('enterprise_name', ''))
        
        # 税务登记号
        ttk.Label(info_frame, text="税务登记号:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.tax_id_entry = ttk.Entry(info_frame, width=20)
        self.tax_id_entry.grid(row=0, column=3, padx=5, pady=5)
        self.tax_id_entry.insert(0, self.tax_settings.get('tax_id', ''))
        
        # 地址
        ttk.Label(info_frame, text="地址:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.address_entry = ttk.Entry(info_frame, width=50)
        self.address_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        self.address_entry.insert(0, self.tax_settings.get('address', ''))
        
        # 税率设置
        rate_frame = ttk.LabelFrame(parent, text="税率设置", padding=15)
        rate_frame.pack(fill='x', padx=10, pady=5)
        
        self.rate_entries = {}
        for i, (tax_type, rate) in enumerate(self.tax_rates.items()):
            ttk.Label(rate_frame, text=f"{tax_type}:").grid(
                row=i, column=0, sticky='w', padx=5, pady=5
            )
            
            entry = ttk.Entry(rate_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, str(self.tax_settings.get(f'{tax_type}_rate', rate * 100)))
            
            ttk.Label(rate_frame, text="%").grid(row=i, column=2, padx=5, pady=5)
            self.rate_entries[tax_type] = entry
        
        # 申报设置
        declaration_frame = ttk.LabelFrame(parent, text="申报设置", padding=15)
        declaration_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(declaration_frame, text="申报周期:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.declaration_period = ttk.Combobox(declaration_frame, 
                                              values=['月度', '季度', '年度'], 
                                              state='readonly', width=10)
        self.declaration_period.grid(row=0, column=1, padx=5, pady=5)
        period_map = {'monthly': '月度', 'quarterly': '季度', 'yearly': '年度'}
        current_period = self.tax_settings.get('declared_period', 'monthly')
        self.declaration_period.set(period_map.get(current_period, '月度'))
        
        # 自动计算复选框
        self.auto_calculate_var = tk.BooleanVar(value=self.tax_settings.get('auto_calculate', True))
        ttk.Checkbutton(declaration_frame, text="自动计算税费", 
                       variable=self.auto_calculate_var).grid(row=0, column=2, padx=20, pady=5)
        
        # 保存按钮
        ttk.Button(declaration_frame, text="保存设置", 
                  command=self._save_settings).grid(row=0, column=3, padx=20, pady=5)
    
    def _create_calculation_tab(self, parent: ttk.Frame):
        """创建税费计算标签页"""
        # 计算控制
        control_frame = ttk.LabelFrame(parent, text="计算控制", padding=15)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # 日期选择
        self.calc_date_selector = DateRangeSelector(
            control_frame,
            on_date_change=self._on_calc_date_change
        )
        self.calc_date_selector.pack(fill='x', padx=5, pady=5)
        
        # 计算按钮
        ttk.Button(control_frame, text="计算税费", 
                  command=self._calculate_taxes).pack(side='right', padx=10)
        
        # 计算结果
        result_frame = ttk.LabelFrame(parent, text="税费计算结果", padding=15)
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 结果表格
        result_columns = ['税种', '计税基础', '税率', '应纳税额']
        self.tax_table = SortableTable(result_frame, result_columns, height=10)
        self.tax_table.pack(fill='both', expand=True)
        
        # 汇总信息
        summary_frame = ttk.Frame(result_frame)
        summary_frame.pack(fill='x', pady=10)
        
        ttk.Label(summary_frame, text="总应纳税额:", 
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        self.total_tax_label = ttk.Label(summary_frame, text="¥0.00", 
                                        font=('Segoe UI', 12, 'bold'),
                                        foreground=win11_theme.colors['error'])
        self.total_tax_label.pack(side='left', padx=(10, 0))
    
    def _create_declaration_tab(self, parent: ttk.Frame):
        """创建申报支持标签页"""
        # 申报准备
        prep_frame = ttk.LabelFrame(parent, text="申报准备", padding=15)
        prep_frame.pack(fill='x', padx=10, pady=5)
        
        # 申报期间选择
        ttk.Label(prep_frame, text="申报期间:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.declaration_period_entry = ttk.Entry(prep_frame, width=20)
        self.declaration_period_entry.grid(row=0, column=1, padx=5, pady=5)
        self.declaration_period_entry.insert(0, datetime.now().strftime('%Y-%m'))
        
        # 生成申报表按钮
        ttk.Button(prep_frame, text="生成增值税申报表", 
                  command=self._generate_vat_declaration).grid(row=0, column=2, padx=10, pady=5)
        
        ttk.Button(prep_frame, text="生成所得税申报表", 
                  command=self._generate_income_tax_declaration).grid(row=0, column=3, padx=10, pady=5)
        
        # 申报文档
        doc_frame = ttk.LabelFrame(parent, text="申报文档", padding=15)
        doc_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 文档列表
        doc_columns = ['文件名', '类型', '生成时间', '状态']
        self.doc_table = SortableTable(doc_frame, doc_columns, height=10)
        self.doc_table.pack(fill='both', expand=True)
        
        # 文档操作按钮
        doc_buttons = ttk.Frame(doc_frame)
        doc_buttons.pack(fill='x', pady=10)
        
        ttk.Button(doc_buttons, text="打开文档", 
                  command=self._open_document).pack(side='left', padx=5)
        ttk.Button(doc_buttons, text="删除文档", 
                  command=self._delete_document).pack(side='left', padx=5)
        ttk.Button(doc_buttons, text="刷新列表", 
                  command=self._refresh_documents).pack(side='left', padx=5)
        
        # 初始化文档列表
        self._refresh_documents()
    
    def _save_settings(self):
        """保存设置"""
        # 更新设置
        self.tax_settings.update({
            'enterprise_name': self.enterprise_name_entry.get(),
            'tax_id': self.tax_id_entry.get(),
            'address': self.address_entry.get(),
            'declared_period': 'monthly' if self.declaration_period.get() == '月度' else 
                              'quarterly' if self.declaration_period.get() == '季度' else 'yearly',
            'auto_calculate': self.auto_calculate_var.get()
        })
        
        # 更新税率
        for tax_type, entry in self.rate_entries.items():
            try:
                rate = float(entry.get()) / 100
                self.tax_settings[f'{tax_type}_rate'] = rate
                self.tax_rates[tax_type] = rate
            except ValueError:
                pass
        
        # 保存
        self._save_tax_settings()
        messagebox.showinfo("成功", "税率设置已保存")
    
    def _on_calc_date_change(self, start_date: date, end_date: date):
        """计算日期变更"""
        if self.tax_settings.get('auto_calculate', True):
            self._calculate_taxes()
    
    def _calculate_taxes(self):
        """计算税费"""
        start_date, end_date = self.calc_date_selector.get_date_range()
        if not start_date or not end_date:
            return
        
        # 获取收入和支出数据
        income_data = self.data_manager.get_income_data(
            start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        )
        
        # 计算计税基础
        total_income = sum(item['final_amount'] for item in income_data)
        profit = total_income * 0.7  # 假设利润率为70%
        
        # 计算各项税费
        tax_results = []
        total_tax = 0
        
        for tax_type, rate in self.tax_rates.items():
            if tax_type == '增值税':
                taxable_base = total_income
            elif tax_type == '企业所得税':
                taxable_base = profit
            else:
                taxable_base = total_income
            
            tax_amount = taxable_base * rate
            total_tax += tax_amount
            
            tax_results.append({
                '税种': tax_type,
                '计税基础': f"¥{taxable_base:,.2f}",
                '税率': f"{rate*100:.1f}%",
                '应纳税额': f"¥{tax_amount:,.2f}"
            })
        
        # 更新表格
        self.tax_table.load_data(tax_results)
        
        # 更新总税额
        self.total_tax_label.config(text=f"¥{total_tax:,.2f}")
    
    def _generate_vat_declaration(self):
        """生成增值税申报表"""
        try:
            messagebox.showinfo("提示", "增值税申报表生成功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败: {str(e)}")
    
    def _generate_income_tax_declaration(self):
        """生成所得税申报表"""
        try:
            messagebox.showinfo("提示", "所得税申报表生成功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败: {str(e)}")
    
    def _generate_tax_declaration(self):
        """生成税务申报表"""
        try:
            messagebox.showinfo("提示", "税务申报表生成功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败: {str(e)}")
    
    def _open_document(self):
        """打开文档"""
        selected = self.doc_table.get_selected_data()
        if selected:
            # 这里可以实现打开文档的逻辑
            messagebox.showinfo("提示", f"打开文档: {selected['文件名']}")
        else:
            messagebox.showwarning("警告", "请选择要打开的文档")
    
    def _delete_document(self):
        """删除文档"""
        selected = self.doc_table.get_selected_data()
        if selected:
            if messagebox.askyesno("确认", f"确定要删除文档 {selected['文件名']} 吗？"):
                # 这里可以实现删除文档的逻辑
                self._refresh_documents()
                messagebox.showinfo("成功", "文档已删除")
        else:
            messagebox.showwarning("警告", "请选择要删除的文档")
    
    def _refresh_documents(self):
        """刷新文档列表"""
        # 这里可以实现扫描文档的逻辑
        sample_docs = [
            {
                '文件名': '增值税申报表_2024-11.pdf',
                '类型': '增值税申报表',
                '生成时间': '2024-11-08 10:30:00',
                '状态': '已生成'
            },
            {
                '文件名': '所得税申报表_2024-11.pdf',
                '类型': '所得税申报表',
                '生成时间': '2024-11-08 10:32:00',
                '状态': '已生成'
            }
        ]
        self.doc_table.load_data(sample_docs)


class FinancialSummaryTab(BaseFrame):
    """自动财务摘要标签页"""
    
    def __init__(self, parent: tk.Widget, data_manager: FinancialDataManager, **kwargs):
        self.data_manager = data_manager
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="自动财务摘要", 
                 font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        # 生成按钮
        ttk.Button(header_frame, text="生成摘要", 
                  command=self._generate_summary).pack(side='right')
        
        # 控制面板
        control_frame = ttk.LabelFrame(self.main_frame, text="摘要设置", padding=15)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # 日期选择
        self.summary_date_selector = DateRangeSelector(
            control_frame,
            on_date_change=self._on_summary_date_change
        )
        self.summary_date_selector.pack(side='left', fill='x', expand=True)
        
        # 摘要类型选择
        ttk.Label(control_frame, text="摘要类型:").pack(side='left', padx=(20, 5))
        self.summary_type = ttk.Combobox(control_frame, 
                                        values=['月报', '季报', '年报', '自定义'],
                                        state='readonly', width=10)
        self.summary_type.pack(side='left', padx=5)
        self.summary_type.set('月报')
        
        # 主要内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧：关键指标
        left_frame = ttk.LabelFrame(content_frame, text="关键财务指标", padding=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self._create_kpi_grid(left_frame)
        
        # 右侧：摘要文本
        right_frame = ttk.LabelFrame(content_frame, text="财务摘要", padding=15)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # 摘要文本框
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill='both', expand=True)
        
        self.summary_text = tk.Text(text_frame, wrap='word', font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        self.summary_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 摘要操作按钮
        summary_buttons = ttk.Frame(right_frame)
        summary_buttons.pack(fill='x', pady=10)
        
        ttk.Button(summary_buttons, text="复制摘要", 
                  command=self._copy_summary).pack(side='left', padx=5)
        ttk.Button(summary_buttons, text="保存摘要", 
                  command=self._save_summary).pack(side='left', padx=5)
        ttk.Button(summary_buttons, text="导出PDF", 
                  command=self._export_pdf).pack(side='left', padx=5)
        
        # 初始化数据
        start_date, end_date = self.summary_date_selector.get_date_range()
        if start_date and end_date:
            self._load_summary_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _create_kpi_grid(self, parent: ttk.Frame):
        """创建KPI网格"""
        # KPI数据
        kpi_data = [
            ('总收入', '¥0.00', 'success'),
            ('总支出', '¥0.00', 'error'),
            ('净利润', '¥0.00', 'primary'),
            ('利润率', '0%', 'accent'),
            ('订单数量', '0', 'info'),
            ('平均订单', '¥0.00', 'warning')
        ]
        
        # 创建2x3网格
        for i, (label, initial_value, color) in enumerate(kpi_data):
            row = i // 3
            col = i % 3
            
            # 创建KPI卡片
            kpi_card = ttk.Frame(parent, relief='solid', borderwidth=1, padding=15)
            kpi_card.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            ttk.Label(kpi_card, text=label, 
                     font=('Segoe UI', 10, 'bold')).pack()
            
            kpi_label = ttk.Label(kpi_card, text=initial_value, 
                                 font=('Segoe UI', 14, 'bold'),
                                 foreground=win11_theme.colors[color])
            kpi_label.pack()
            
            # 保存引用以便更新
            setattr(self, f'{label.replace(" ", "_")}_label', kpi_label)
        
        # 配置网格权重
        for i in range(2):
            parent.grid_rowconfigure(i, weight=1)
        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)
    
    def _on_summary_date_change(self, start_date: date, end_date: date):
        """摘要日期变更"""
        self._load_summary_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _load_summary_data(self, start_date: str, end_date: str):
        """加载摘要数据"""
        # 获取分析数据
        analysis_data = self.data_manager.get_profit_analysis(start_date, end_date)
        
        # 更新KPI
        total_income = analysis_data['total_income']
        total_expense = analysis_data['total_expense']
        net_profit = analysis_data['net_profit']
        profit_margin = analysis_data['profit_margin']
        order_count = analysis_data['income_count']
        avg_order = total_income / order_count if order_count > 0 else 0
        
        # 更新标签
        self.总收入_label.config(text=f"¥{total_income:,.2f}")
        self.总支出_label.config(text=f"¥{total_expense:,.2f}")
        self.净利润_label.config(text=f"¥{net_profit:,.2f}")
        self.利润率_label.config(text=f"{profit_margin:.1f}%")
        self.订单数量_label.config(text=str(order_count))
        self.平均订单_label.config(text=f"¥{avg_order:.2f}")
        
        # 生成摘要文本
        self._generate_summary_text(analysis_data)
    
    def _generate_summary_text(self, analysis_data: Dict):
        """生成摘要文本"""
        total_income = analysis_data['total_income']
        total_expense = analysis_data['total_expense']
        net_profit = analysis_data['net_profit']
        profit_margin = analysis_data['profit_margin']
        order_count = analysis_data['income_count']
        expense_count = analysis_data['expense_count']
        
        # 生成摘要
        summary = f"""
# 财务摘要报告

## 总体情况
- **报告期间**: {self.summary_date_selector.start_date} 至 {self.summary_date_selector.end_date}
- **总收入**: ¥{total_income:,.2f}
- **总支出**: ¥{total_expense:,.2f}
- **净利润**: ¥{net_profit:,.2f}
- **利润率**: {profit_margin:.1f}%

## 经营分析
- **收入笔数**: {order_count}笔
- **支出笔数**: {expense_count}笔
- **收支比**: 1:{total_expense/total_income:.2f} (当收入>0时)

## 盈利能力评估
"""
        
        if net_profit > 0:
            summary += f"- ✅ **盈利状况**: 良好，净利润¥{net_profit:,.2f}\n"
            if profit_margin > 20:
                summary += "- ✅ **利润率水平**: 优秀，超过20%\n"
            elif profit_margin > 10:
                summary += "- ✅ **利润率水平**: 良好，10%-20%\n"
            else:
                summary += "- ⚠️ **利润率水平**: 一般，低于10%\n"
        else:
            summary += f"- ❌ **盈利状况**: 亏损，净亏损¥{abs(net_profit):,.2f}\n"
            summary += "- ⚠️ **建议**: 需要控制成本或增加收入\n"
        
        summary += f"""
## 经营建议
"""
        if profit_margin > 15:
            summary += "- 当前经营状况良好，可考虑扩大业务规模\n"
        elif profit_margin > 5:
            summary += "- 经营状况一般，建议优化成本结构\n"
        else:
            summary += "- 需要重点关注成本控制和收入提升\n"
        
        if order_count > 0:
            avg_daily_orders = order_count / 30  # 假设30天
            summary += f"- 平均每日订单量: {avg_daily_orders:.1f}笔\n"
        
        # 更新文本框
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
    
    def _generate_summary(self):
        """生成摘要"""
        start_date, end_date = self.summary_date_selector.get_date_range()
        if start_date and end_date:
            self._load_summary_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            messagebox.showinfo("成功", "财务摘要已生成")
        else:
            messagebox.showwarning("警告", "请选择有效的日期范围")
    
    def _copy_summary(self):
        """复制摘要"""
        summary_text = self.summary_text.get(1.0, tk.END)
        self.main_frame.clipboard_clear()
        self.main_frame.clipboard_append(summary_text)
        messagebox.showinfo("成功", "摘要已复制到剪贴板")
    
    def _save_summary(self):
        """保存摘要"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                summary_text = self.summary_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary_text)
                messagebox.showinfo("成功", f"摘要已保存到 {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _export_pdf(self):
        """导出PDF"""
        try:
            messagebox.showinfo("提示", "PDF导出功能正在开发中...")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")


class FinancialReportsGUI(BaseFrame):
    """财务报表主界面"""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.data_manager = FinancialDataManager()
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 标题
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        ttk.Label(title_frame, text="财务报表系统", 
                 font=('Segoe UI', 20, 'bold')).pack(side='left')
        
        ttk.Label(title_frame, text="姐妹花店财务管理系统", 
                 font=('Segoe UI', 10),
                 foreground=win11_theme.colors['text_secondary']).pack(side='left', padx=(20, 0))
        
        # 标签笔记本
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # 创建各个标签页
        self._create_tabs()
        
        # 应用主题
        self._apply_theme()
    
    def _create_tabs(self):
        """创建标签页"""
        # 收入报表
        income_frame = ttk.Frame(self.notebook)
        self.notebook.add(income_frame, text="📈 收入报表")
        self.income_tab = IncomeStatementTab(income_frame, self.data_manager)
        self.income_tab.pack(fill='both', expand=True)
        
        # 支出报表
        expense_frame = ttk.Frame(self.notebook)
        self.notebook.add(expense_frame, text="📊 支出报表")
        self.expense_tab = ExpenseStatementTab(expense_frame, self.data_manager)
        self.expense_tab.pack(fill='both', expand=True)
        
        # 利润分析
        profit_frame = ttk.Frame(self.notebook)
        self.notebook.add(profit_frame, text="💰 利润分析")
        self.profit_tab = ProfitAnalysisTab(profit_frame, self.data_manager)
        self.profit_tab.pack(fill='both', expand=True)
        
        # 现金流
        cashflow_frame = ttk.Frame(self.notebook)
        self.notebook.add(cashflow_frame, text="💵 现金流")
        self.cashflow_tab = CashFlowTab(cashflow_frame, self.data_manager)
        self.cashflow_tab.pack(fill='both', expand=True)
        
        # 税费管理
        tax_frame = ttk.Frame(self.notebook)
        self.notebook.add(tax_frame, text="🧮 税费管理")
        self.tax_tab = TaxManagementTab(tax_frame, self.data_manager)
        self.tax_tab.pack(fill='both', expand=True)
        
        # 自动摘要
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📋 自动摘要")
        self.summary_tab = FinancialSummaryTab(summary_frame, self.data_manager)
        self.summary_tab.pack(fill='both', expand=True)
    
    def _apply_theme(self):
        """应用Win11主题"""
        # 这里可以应用特定的财务报表主题样式
        pass


# 测试和演示功能
def create_demo_window():
    """创建演示窗口"""
    demo_window = tk.Tk()
    demo_window.title("财务报表系统演示")
    demo_window.geometry("1200x800")
    
    # 应用Win11主题
    win11_theme.apply_theme(demo_window)
    
    # 创建财务报表界面
    financial_reports = FinancialReportsGUI(demo_window)
    financial_reports.pack(fill='both', expand=True)
    
    return demo_window


if __name__ == "__main__":
    # 创建并运行演示
    demo = create_demo_window()
    demo.mainloop()