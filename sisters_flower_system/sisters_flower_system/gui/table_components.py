"""
表格组件
提供高级表格功能
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional
from .base_components import BaseTreeview, BaseFrame, BaseButton

# 导入工具函数
try:
    from ..utils.gui_utils import make_table
except ImportError:
    # 处理相对导入问题
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.gui_utils import make_table


class ScrollableTable(BaseFrame):
    """可滚动的表格组件"""
    
    def __init__(self, parent: tk.Widget, columns: List[str], 
                 data: List[Dict[str, Any]] = None, **kwargs):
        self.columns = columns
        self.data = data or []
        self.data_map: Dict[str, Dict[str, Any]] = {}  # 存储原始数据
        self.selected_callback: Optional[Callable] = None
        self.double_click_callback: Optional[Callable] = None
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 创建主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 创建表格
        self.tree, self.container = make_table(self.main_frame, self.columns)
        
        # 绑定事件
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # 包装容器
        self.container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 加载初始数据
        if self.data:
            self.load_data(self.data)
    
    def load_data(self, data: List[Dict[str, Any]]):
        """加载数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.data_map.clear()
        
        # 添加新数据
        for i, row_data in enumerate(data):
            item_id = str(i)
            values = tuple(row_data.get(col, '') for col in self.columns)
            self.tree.insert('', 'end', iid=item_id, values=values)
            self.data_map[item_id] = row_data
    
    def add_row(self, data: Dict[str, Any]):
        """添加行"""
        item_id = str(len(self.data_map))
        values = tuple(data.get(col, '') for col in self.columns)
        self.tree.insert('', 'end', iid=item_id, values=values)
        self.data_map[item_id] = data
    
    def remove_row(self, item_id: str):
        """删除行"""
        if item_id in self.data_map:
            self.tree.delete(item_id)
            del self.data_map[item_id]
    
    def update_row(self, item_id: str, data: Dict[str, Any]):
        """更新行"""
        if item_id in self.data_map:
            values = tuple(data.get(col, '') for col in self.columns)
            self.tree.item(item_id, values=values)
            self.data_map[item_id] = data
    
    def get_selected_data(self) -> Optional[Dict[str, Any]]:
        """获取选中行的数据"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            return self.data_map.get(item_id)
        return None
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """获取所有数据"""
        return list(self.data_map.values())
    
    def set_selected_callback(self, callback: Callable):
        """设置选择回调"""
        self.selected_callback = callback
    
    def set_double_click_callback(self, callback: Callable):
        """设置双击回调"""
        self.double_click_callback = callback
    
    def _on_select(self, event):
        """选择事件处理"""
        if self.selected_callback:
            data = self.get_selected_data()
            if data:
                self.selected_callback(data)
    
    def _on_double_click(self, event):
        """双击事件处理"""
        if self.double_click_callback:
            data = self.get_selected_data()
            if data:
                self.double_click_callback(data)


class PaginatedTable(BaseFrame):
    """分页表格组件"""
    
    def __init__(self, parent: tk.Widget, columns: List[str], 
                 page_size: int = 20, **kwargs):
        self.columns = columns
        self.page_size = page_size
        self.current_page = 1
        self.total_pages = 1
        self.all_data: List[Dict[str, Any]] = []
        self.current_data: List[Dict[str, Any]] = []
        self.page_change_callback: Optional[Callable] = None
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 创建主容器
        self.main_frame = ttk.Frame(self.parent)
        self.widget = self.main_frame
        
        # 创建表格
        self.table = ScrollableTable(self.main_frame, self.columns)
        self.table.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建分页控制器
        self._create_pagination_controls()
    
    def _create_pagination_controls(self):
        """创建分页控制器"""
        # 分页控制容器
        pagination_frame = ttk.Frame(self.main_frame)
        pagination_frame.pack(fill='x', padx=5, pady=5)
        
        # 上一页按钮
        self.prev_btn = ttk.Button(
            pagination_frame, 
            text="上一页", 
            command=self._prev_page
        )
        self.prev_btn.pack(side='left', padx=5)
        
        # 页码标签
        self.page_label = ttk.Label(pagination_frame, text="第 1 页 / 共 1 页")
        self.page_label.pack(side='left', padx=10)
        
        # 下一页按钮
        self.next_btn = ttk.Button(
            pagination_frame, 
            text="下一页", 
            command=self._next_page
        )
        self.next_btn.pack(side='left', padx=5)
        
        # 跳转到指定页
        ttk.Label(pagination_frame, text="跳转到:").pack(side='right', padx=5)
        self.page_entry = ttk.Entry(pagination_frame, width=5)
        self.page_entry.pack(side='right', padx=5)
        
        ttk.Button(
            pagination_frame, 
            text="跳转", 
            command=self._go_to_page
        ).pack(side='right', padx=5)
    
    def load_data(self, data: List[Dict[str, Any]]):
        """加载数据并分页"""
        self.all_data = data
        self.total_pages = (len(data) + self.page_size - 1) // self.page_size
        self.current_page = 1
        self._update_page()
    
    def _update_page(self):
        """更新当前页数据"""
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        self.current_data = self.all_data[start_idx:end_idx]
        
        # 更新表格
        self.table.load_data(self.current_data)
        
        # 更新页码显示
        self.page_label.config(text=f"第 {self.current_page} 页 / 共 {self.total_pages} 页")
        
        # 更新按钮状态
        self.prev_btn.config(state='normal' if self.current_page > 1 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < self.total_pages else 'disabled')
        
        # 回调
        if self.page_change_callback:
            self.page_change_callback(self.current_page, self.total_pages, self.current_data)
    
    def _prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_page()
    
    def _next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_page()
    
    def _go_to_page(self):
        """跳转到指定页"""
        try:
            page = int(self.page_entry.get())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self._update_page()
        except ValueError:
            pass
    
    def get_current_data(self) -> List[Dict[str, Any]]:
        """获取当前页数据"""
        return self.current_data
    
    def set_page_change_callback(self, callback: Callable):
        """设置页码变化回调"""
        self.page_change_callback = callback


class SortableTable(ScrollableTable):
    """可排序表格组件"""
    
    def __init__(self, parent: tk.Widget, columns: List[str], **kwargs):
        self.sort_column = None
        self.sort_reverse = False
        super().__init__(parent, columns, **kwargs)
    
    def create_widget(self):
        super().create_widget()
        
        # 为每个列标题添加排序功能
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))
    
    def _sort_by_column(self, column: str):
        """按列排序"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # 排序数据
        sorted_data = sorted(
            list(self.data_map.values()),
            key=lambda x: self._get_sort_key(x.get(column, '')),
            reverse=self.sort_reverse
        )
        
        # 重新加载数据
        self.load_data(sorted_data)
    
    def _get_sort_key(self, value) -> Any:
        """获取排序键"""
        if isinstance(value, (int, float)):
            return value
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return int(value)
            except (ValueError, TypeError):
                return str(value).lower()
