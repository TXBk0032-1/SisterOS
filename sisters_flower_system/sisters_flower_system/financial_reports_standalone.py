"""
独立财务报表模块
可以独立运行的财务报表系统
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import json
from typing import List, Dict, Any, Optional
import calendar

# 尝试导入matplotlib，如果失败则禁用图表功能
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("提示: 未安装matplotlib，图表功能将不可用")


# Win11主题颜色
class Win11Theme:
    """简化版Win11主题"""
    COLORS = {
        'primary': '#0067C0',
        'secondary': '#A4D5FF',
        'accent': '#4CC2FF',
        'background': '#FFFFFF',
        'surface': '#F8F9FA',
        'surface_elevated': '#FFFFFF',
        'text_primary': '#000000',
        'text_secondary': '#605E5C',
        'text_disabled': '#A19F9D',
        'border': '#E1DFDD',
        'success': '#107C10',
        'warning': '#FF8C00',
        'error': '#D13438',
        'info': '#0078D4'
    }


class MockDataManager:
    """模拟数据管理器，用于演示"""
    
    def get_income_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取模拟收入数据"""
        # 生成模拟数据
        import random
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        data = []
        current = start
        order_id = 1
        
        while current <= end:
            # 每天1-5个订单
            for _ in range(random.randint(1, 5)):
                data.append({
                    'id': order_id,
                    'sale_date': current.strftime('%Y-%m-%d'),
                    'total_amount': random.uniform(50, 500),
                    'discount_amount': random.uniform(0, 50),
                    'final_amount': 0,  # 稍后计算
                    'payment_method': random.choice(['现金', '微信', '支付宝', '银行卡']),
                    'notes': '',
                    'item_count': random.randint(1, 10)
                })
                order_id += 1
            
            current += timedelta(days=1)
        
        # 计算最终金额
        for item in data:
            item['final_amount'] = item['total_amount'] - item['discount_amount']
        
        return data
    
    def get_expense_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取模拟支出数据"""
        import random
        from datetime import datetime, timedelta
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        categories = ['租金', '水电费', '员工工资', '采购成本', '运输费', '广告费', '其他']
        payment_methods = ['现金', '银行卡', '转账']
        
        data = []
        expense_id = 1
        current = start
        
        while current <= end:
            # 每天0-2笔支出
            for _ in range(random.randint(0, 2)):
                data.append({
                    'id': expense_id,
                    'expense_date': current.strftime('%Y-%m-%d'),
                    'category': random.choice(categories),
                    'amount': random.uniform(20, 800),
                    'description': f"{random.choice(categories)}支出",
                    'payment_method': random.choice(payment_methods)
                })
                expense_id += 1
            
            current += timedelta(days=1)
        
        return data
    
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


class DateRangeSelector(tk.Frame):
    """日期范围选择器"""
    
    def __init__(self, parent, on_date_change=None):
        super().__init__(parent)
        self.on_date_change = on_date_change
        self.start_date = None
        self.end_date = None
        self._create_widgets()
    
    def _create_widgets(self):
        # 标题
        tk.Label(self, text="日期范围:", font=('微软雅黑', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        # 开始日期
        tk.Label(self, text="从:").pack(side='left')
        self.start_entry = tk.Entry(self, width=12)
        self.start_entry.pack(side='left', padx=(5, 15))
        
        # 结束日期
        tk.Label(self, text="到:").pack(side='left')
        self.end_entry = tk.Entry(self, width=12)
        self.end_entry.pack(side='left', padx=(5, 15))
        
        # 预设按钮
        buttons_frame = tk.Frame(self)
        buttons_frame.pack(side='left', padx=15)
        
        tk.Button(buttons_frame, text="本月", command=lambda: self._set_date_range('current_month')).pack(side='left', padx=2)
        tk.Button(buttons_frame, text="上月", command=lambda: self._set_date_range('last_month')).pack(side='left', padx=2)
        tk.Button(buttons_frame, text="本季度", command=lambda: self._set_date_range('current_quarter')).pack(side='left', padx=2)
        tk.Button(buttons_frame, text="本年", command=lambda: self._set_date_range('current_year')).pack(side='left', padx=2)
        
        # 设置默认值为本月
        self._set_date_range('current_month')
        
        # 绑定变更事件
        self.start_entry.bind('<FocusOut>', self._on_date_change)
        self.end_entry.bind('<FocusOut>', self._on_date_change)
    
    def _set_date_range(self, period):
        """设置日期范围"""
        today = date.today()
        
        if period == 'current_month':
            self.start_date = today.replace(day=1)
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
    
    def get_date_range(self):
        """获取日期范围"""
        return self.start_date, self.end_date


class ChartCanvas(tk.Frame):
    """图表画布组件"""
    
    def __init__(self, parent, chart_type='line'):
        super().__init__(parent)
        self.chart_type = chart_type
        self.figure = None
        self.canvas = None
        self._create_widgets()
    
    def _create_widgets(self):
        if not HAS_MATPLOTLIB:
            # 如果没有matplotlib，显示提示信息
            tk.Label(self, 
                    text="需要安装matplotlib才能显示图表\npip install matplotlib",
                    font=('微软雅黑', 12),
                    fg=Win11Theme.COLORS['error']).pack(expand=True)
            return
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def plot_line_chart(self, x_data, y_data, title, x_label, y_label):
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
    
    def plot_bar_chart(self, x_data, y_data, title, x_label, y_label):
        """绘制柱状图"""
        if not HAS_MATPLOTLIB or not self.figure:
            return
        
        self.ax.clear()
        self.ax.bar(x_data, y_data, color=Win11Theme.COLORS['primary'], alpha=0.7)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(True, alpha=0.3, axis='y')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_pie_chart(self, data, labels, title):
        """绘制饼图"""
        if not HAS_MATPLOTLIB or not self.figure:
            return
        
        self.ax.clear()
        colors = [Win11Theme.COLORS['primary'], Win11Theme.COLORS['secondary'], 
                 Win11Theme.COLORS['accent'], Win11Theme.COLORS['success'],
                 Win11Theme.COLORS['warning'], Win11Theme.COLORS['error']]
        
        self.ax.pie(data, labels=labels, autopct='%1.1f%%', 
                   colors=colors[:len(data)], startangle=90)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.figure.tight_layout()
        self.canvas.draw()


class SimpleTable(tk.Frame):
    """简单的表格组件"""
    
    def __init__(self, parent, columns, height=10):
        super().__init__(parent)
        self.columns = columns
        self.height = height
        self.data = []
        self._create_widgets()
    
    def _create_widgets(self):
        # 创建Treeview
        self.tree = ttk.Treeview(self, columns=self.columns, show='headings', height=self.height)
        
        # 添加滚动条
        scrollbar_v = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # 配置列
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def load_data(self, data):
        """加载数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.data = data
        
        # 添加新数据
        for row_data in data:
            values = tuple(row_data.get(col, '') for col in self.columns)
            self.tree.insert('', 'end', values=values)
    
    def get_selected_data(self):
        """获取选中行的数据"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            return self.data[int(item_id)]
        return None


class IncomeStatementTab(tk.Frame):
    """收入财务报表标签页"""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.data_manager = data_manager
        self._create_widgets()
    
    def _create_widgets(self):
        # 标题
        header_frame = tk.Frame(self)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(header_frame, text="收入财务报表", 
                font=('微软雅黑', 16, 'bold')).pack(side='left')
        
        # 导出按钮
        tk.Button(header_frame, text="导出Excel", 
                 command=self._export_excel).pack(side='right')
        
        # 日期选择器
        self.date_selector = DateRangeSelector(
            self, 
            on_date_change=self._on_date_change
        )
        self.date_selector.pack(fill='x', padx=20, pady=10)
        
        # 主要内容区域
        content_frame = tk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 左侧：收入明细表格
        left_frame = tk.LabelFrame(content_frame, text="收入明细", font=('微软雅黑', 10, 'bold'))
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 收入明细表格
        income_columns = ['日期', '订单号', '商品数量', '原价', '折扣', '实收金额', '支付方式', '备注']
        self.income_table = SimpleTable(left_frame, income_columns, height=15)
        self.income_table.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 右侧：图表区域
        right_frame = tk.LabelFrame(content_frame, text="收入趋势图", font=('微软雅黑', 10, 'bold'))
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.chart_canvas = ChartCanvas(right_frame, 'line')
        self.chart_canvas.pack(fill='both', expand=True)
        
        # 初始化数据
        start_date, end_date = self.date_selector.get_date_range()
        if start_date and end_date:
            self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _on_date_change(self, start_date, end_date):
        """日期变更事件"""
        self._load_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    def _load_data(self, start_date, end_date):
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
        
        # 绘制图表
        if HAS_MATPLOTLIB and table_data:
            self._plot_income_chart(table_data)
    
    def _plot_income_chart(self, data):
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
        messagebox.showinfo("提示", "Excel导出功能正在开发中...")


class FinancialReportsGUI(tk.Frame):
    """财务报表主界面"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.data_manager = MockDataManager()
        self._create_widgets()
    
    def _create_widgets(self):
        # 标题
        title_frame = tk.Frame(self)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="财务报表系统", 
                font=('微软雅黑', 20, 'bold')).pack(side='left')
        
        tk.Label(title_frame, text="姐妹花店财务管理系统", 
                font=('微软雅黑', 10),
                fg=Win11Theme.COLORS['text_secondary']).pack(side='left', padx=(20, 0))
        
        # 标签笔记本
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        # 创建各个标签页
        self._create_tabs()
    
    def _create_tabs(self):
        # 收入报表
        income_frame = tk.Frame(self.notebook)
        self.notebook.add(income_frame, text="📈 收入报表")
        self.income_tab = IncomeStatementTab(income_frame, self.data_manager)
        self.income_tab.pack(fill='both', expand=True)
        
        # 支出报表 (简化版)
        expense_frame = tk.Frame(self.notebook)
        self.notebook.add(expense_frame, text="📊 支出报表")
        tk.Label(expense_frame, text="支出报表功能开发中...", 
                font=('微软雅黑', 14)).pack(expand=True)
        
        # 利润分析 (简化版)
        profit_frame = tk.Frame(self.notebook)
        self.notebook.add(profit_frame, text="💰 利润分析")
        tk.Label(profit_frame, text="利润分析功能开发中...", 
                font=('微软雅黑', 14)).pack(expand=True)
        
        # 现金流 (简化版)
        cashflow_frame = tk.Frame(self.notebook)
        self.notebook.add(cashflow_frame, text="💵 现金流")
        tk.Label(cashflow_frame, text="现金流功能开发中...", 
                font=('微软雅黑', 14)).pack(expand=True)
        
        # 税费管理 (简化版)
        tax_frame = tk.Frame(self.notebook)
        self.notebook.add(tax_frame, text="🧮 税费管理")
        tk.Label(tax_frame, text="税费管理功能开发中...", 
                font=('微软雅黑', 14)).pack(expand=True)


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    root.title("姐妹花店 - 财务报表系统")
    root.geometry("1400x900")
    
    # 设置窗口图标（如果有的话）
    # root.iconbitmap('icon.ico')
    
    # 创建财务报表界面
    financial_reports = FinancialReportsGUI(root)
    financial_reports.pack(fill='both', expand=True)
    
    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()