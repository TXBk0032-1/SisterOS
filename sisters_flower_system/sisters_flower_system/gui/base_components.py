"""
基础组件
所有GUI组件的基类和通用功能
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Dict, List
try:
    from ..config.settings import SCALE_FACTOR
except ImportError:
    # 直接从settings模块导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import SCALE_FACTOR


class BaseComponent(ABC):
    """所有GUI组件的基类"""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.parent = parent
        self.widget = None
        self._config = kwargs
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._style_config = {}
        self._is_initialized = False
    
    @abstractmethod
    def create_widget(self):
        """创建组件的核心方法，子类必须实现"""
        pass
    
    def initialize(self):
        """初始化组件"""
        if not self._is_initialized:
            self.create_widget()
            self._apply_config()
            self._apply_style()
            self._bind_events()
            self._is_initialized = True
    
    def _apply_config(self):
        """应用配置参数"""
        if self.widget and self._config:
            for key, value in self._config.items():
                if hasattr(self.widget, key):
                    try:
                        if callable(value):
                            # 如果值是可调用的，将其作为事件绑定
                            self.bind(key[3:] if key.startswith('on_') else key, value)
                        else:
                            setattr(self.widget, key, value)
                    except Exception as e:
                        print(f"应用配置失败 {key}: {e}")
    
    def _apply_style(self):
        """应用样式配置"""
        if self.widget and self._style_config:
            # 应用样式配置
            for key, value in self._style_config.items():
                try:
                    if hasattr(self.widget, 'configure'):
                        self.widget.configure(**{key: value})
                except Exception as e:
                    print(f"应用样式失败 {key}: {e}")
    
    def _bind_events(self):
        """绑定事件处理程序"""
        for event, handlers in self._event_handlers.items():
            for handler in handlers:
                self.widget.bind(event, handler)
    
    def bind(self, event: str, handler: Callable):
        """绑定事件处理程序"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self.event_add(event, handler)
    
    def event_add(self, event: str, handler: Callable):
        """添加事件处理程序"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def configure(self, **kwargs):
        """配置组件"""
        self._config.update(kwargs)
        if self._is_initialized:
            self._apply_config()
    
    def pack(self, **kwargs):
        """包装组件"""
        if self.widget:
            return self.widget.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局组件"""
        if self.widget:
            return self.widget.grid(**kwargs)
    
    def place(self, **kwargs):
        """绝对定位组件"""
        if self.widget:
            return self.widget.place(**kwargs)
    
    def show(self):
        """显示组件"""
        if self.widget:
            self.widget.pack(fill='both', expand=True)
    
    def hide(self):
        """隐藏组件"""
        if self.widget:
            self.widget.pack_forget()
    
    def destroy(self):
        """销毁组件"""
        if self.widget:
            self.widget.destroy()
            self.widget = None
        self._event_handlers.clear()


class BaseFrame(BaseComponent):
    """基础框架组件"""
    
    def create_widget(self):
        self.widget = ttk.Frame(self.parent)


class BaseWindow(BaseComponent):
    """基础窗口组件"""
    
    def __init__(self, title: str = "", **kwargs):
        self.title = title
        super().__init__(None, **kwargs)
        self.root = tk.Tk()
        self.root.title(title)
        
        # 设置窗口属性
        if 'width' in kwargs:
            self.root.geometry(f"{kwargs['width']}x{kwargs.get('height', 400)}")
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widget(self):
        # BaseWindow不使用父组件，直接使用root
        pass
    
    def on_close(self):
        """窗口关闭事件"""
        self.root.destroy()
    
    def mainloop(self):
        """启动主循环"""
        self.root.mainloop()
    
    def withdraw(self):
        """隐藏窗口"""
        self.root.withdraw()
    
    def deiconify(self):
        """显示窗口"""
        self.root.deiconify()


class BaseButton(BaseComponent):
    """基础按钮组件"""
    
    def create_widget(self):
        self.widget = ttk.Button(
            self.parent,
            text=self._config.get('text', 'Button'),
            style=self._config.get('style', 'TButton')
        )


class BaseEntry(BaseComponent):
    """基础输入框组件"""
    
    def create_widget(self):
        entry_type = self._config.get('type', 'text')
        if entry_type == 'password':
            self.widget = ttk.Entry(
                self.parent,
                show='*',
                font=self._config.get('font')
            )
        else:
            self.widget = ttk.Entry(
                self.parent,
                font=self._config.get('font')
            )
    
    def get(self) -> str:
        """获取输入值"""
        if self.widget:
            return self.widget.get()
        return ""
    
    def set(self, value: str):
        """设置输入值"""
        if self.widget:
            self.widget.delete(0, tk.END)
            self.widget.insert(0, value)


class BaseLabel(BaseComponent):
    """基础标签组件"""
    
    def create_widget(self):
        self.widget = ttk.Label(
            self.parent,
            text=self._config.get('text', ''),
            style=self._config.get('style', 'TLabel')
        )
    
    def set_text(self, text: str):
        """设置标签文本"""
        if self.widget:
            self.widget.config(text=text)


class BaseTreeview(BaseComponent):
    """基础表格组件"""
    
    def __init__(self, parent: tk.Widget, columns: List[str] = None, **kwargs):
        self.columns = columns or []
        super().__init__(parent, **kwargs)
    
    def create_widget(self):
        # 创建容器
        self.container = ttk.Frame(self.parent)
        
        # 创建滚动条
        self.vsb = ttk.Scrollbar(self.container, orient="vertical")
        self.hsb = ttk.Scrollbar(self.container, orient="horizontal")
        
        # 创建Treeview
        self.widget = ttk.Treeview(
            self.container,
            columns=self.columns,
            show='headings',
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set
        )
        
        # 配置滚动条
        self.vsb.config(command=self.widget.yview)
        self.hsb.config(command=self.widget.xview)
        
        # 配置列
        for col in self.columns:
            self.widget.heading(col, text=col)
            self.widget.column(col, width=int(100 * SCALE_FACTOR))
        
        # 布局
        self.widget.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
    
    def insert(self, parent: str = "", index: str = "end", values: tuple = ()) -> str:
        """插入行"""
        if self.widget:
            return self.widget.insert(parent, index, values=values)
    
    def delete(self, item: str):
        """删除行"""
        if self.widget:
            self.widget.delete(item)
    
    def get_children(self, item: str = "") -> tuple:
        """获取子项"""
        if self.widget:
            return self.widget.get_children(item)
    
    def item(self, item: str, option: str = None):
        """获取或设置项目信息"""
        if self.widget:
            return self.widget.item(item, option)
    
    def focus(self, item: str = ""):
        """聚焦到项目"""
        if self.widget:
            self.widget.focus(item)
    
    def selection(self) -> tuple:
        """获取选中的项目"""
        if self.widget:
            return self.widget.selection()
    
    def set(self, item: str, column: str, value: str):
        """设置项目值"""
        if self.widget:
            self.widget.set(item, column, value)
    
    def pack(self, **kwargs):
        """包装容器"""
        if self.container:
            return self.container.pack(**kwargs)


class BaseDialog(BaseWindow):
    """基础对话框"""
    
    def __init__(self, title: str, parent: tk.Widget, **kwargs):
        self.parent = parent
        self.result = None
        super().__init__(title, **kwargs)
        
        # 设置对话框属性
        self.root.transient(parent)
        self.root.grab_set()  # 模态对话框
        self.root.resizable(False, False)
    
    def show(self) -> Any:
        """显示对话框并返回结果"""
        self.root.deiconify()
        self.root.wait_window()
        return self.result
    
    def set_result(self, result: Any):
        """设置对话框结果"""
        self.result = result
        self.root.destroy()
