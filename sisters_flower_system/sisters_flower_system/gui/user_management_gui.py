#!/usr/bin/env python3
"""
用户管理界面模块
提供完整的用户管理功能，包括用户CRUD、权限管理、活动日志等
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_components import BaseFrame, BaseButton, BaseEntry, BaseLabel, BaseTreeview, BaseDialog
from ..config.win11_theme import win11_theme
from ..config.settings import SCALE_FACTOR


class User:
    """用户数据模型"""
    
    def __init__(self, user_id: int, username: str, email: str, role: str = "user", 
                 status: str = "active", created_at: str = None, last_login: str = None,
                 permissions: List[str] = None, phone: str = "", department: str = ""):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_login = last_login
        self.permissions = permissions or []
        self.phone = phone
        self.department = department
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'permissions': self.permissions,
            'phone': self.phone,
            'department': self.department
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建用户"""
        return cls(**data)


class ActivityLog:
    """活动日志数据模型"""
    
    def __init__(self, log_id: int, user_id: int, action: str, details: str, 
                 timestamp: str = None, ip_address: str = ""):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action
        self.details = details
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ip_address = ip_address
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp,
            'ip_address': self.ip_address
        }


class UserFormDialog(BaseDialog):
    """用户表单对话框"""
    
    def __init__(self, parent: tk.Widget, user: User = None):
        self.user = user
        self.result = None
        super().__init__("创建用户" if not user else "编辑用户", parent, width=500, height=600)
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def create_widget(self):
        """创建表单组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title = "创建新用户" if not self.user else "编辑用户"
        title_label = ttk.Label(main_frame, text=title, font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 创建滚动框架
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 表单字段
        self._create_form_fields(scrollable_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill='x')
        
        # 确定按钮
        confirm_btn = ttk.Button(
            button_frame, 
            text="确定", 
            command=self.confirm,
            style='Accent.TButton'
        )
        confirm_btn.pack(side='right', padx=(10, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(
            button_frame, 
            text="取消", 
            command=self.cancel
        )
        cancel_btn.pack(side='right')
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
    
    def _create_form_fields(self, parent):
        """创建表单字段"""
        self.entries = {}
        
        # 用户名字段
        self._create_field(parent, "用户名", "username", "必填，请输入用户名")
        
        # 邮箱字段
        self._create_field(parent, "邮箱", "email", "必填，请输入邮箱地址")
        
        # 密码字段
        if not self.user:
            self._create_field(parent, "密码", "password", "必填，请输入密码", entry_type="password")
        
        # 手机号字段
        self._create_field(parent, "手机号", "phone", "可选，请输入手机号")
        
        # 部门字段
        self._create_field(parent, "部门", "department", "可选，请输入所属部门")
        
        # 角色选择
        self._create_role_field(parent)
        
        # 状态选择
        self._create_status_field(parent)
        
        # 权限设置
        self._create_permissions_field(parent)
        
        # 如果是编辑模式，填充现有数据
        if self.user:
            self._populate_form()
    
    def _create_field(self, parent, label_text: str, field_name: str, 
                     placeholder: str, entry_type: str = "text"):
        """创建输入字段"""
        # 标签
        label = ttk.Label(parent, text=label_text, font=('Segoe UI', 10, 'bold'))
        label.pack(anchor='w', pady=(15, 5))
        
        # 输入框
        if entry_type == "password":
            entry = ttk.Entry(parent, show='*', font=('Segoe UI', 10))
        else:
            entry = ttk.Entry(parent, font=('Segoe UI', 10))
        entry.pack(fill='x', pady=(0, 5))
        
        # 提示文字
        if placeholder:
            hint_label = ttk.Label(parent, text=placeholder, font=('Segoe UI', 8))
            hint_label.pack(anchor='w', pady=(0, 10))
            hint_label.configure(foreground='gray')
        
        self.entries[field_name] = entry
    
    def _create_role_field(self, parent):
        """创建角色选择字段"""
        # 标签
        label = ttk.Label(parent, text="用户角色", font=('Segoe UI', 10, 'bold'))
        label.pack(anchor='w', pady=(15, 5))
        
        # 角色选择
        role_frame = ttk.Frame(parent)
        role_frame.pack(fill='x', pady=(0, 5))
        
        self.role_var = tk.StringVar(value="user")
        roles = [
            ("普通用户", "user"),
            ("管理员", "admin"),
            ("经理", "manager"),
            ("财务", "accountant"),
            ("销售", "sales")
        ]
        
        for text, value in roles:
            rb = ttk.Radiobutton(role_frame, text=text, variable=self.role_var, value=value)
            rb.pack(anchor='w', pady=2)
    
    def _create_status_field(self, parent):
        """创建状态选择字段"""
        # 标签
        label = ttk.Label(parent, text="账户状态", font=('Segoe UI', 10, 'bold'))
        label.pack(anchor='w', pady=(15, 5))
        
        # 状态选择
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill='x', pady=(0, 5))
        
        self.status_var = tk.StringVar(value="active")
        statuses = [
            ("活跃", "active"),
            ("禁用", "disabled"),
            ("待审核", "pending")
        ]
        
        for text, value in statuses:
            rb = ttk.Radiobutton(status_frame, text=text, variable=self.status_var, value=value)
            rb.pack(anchor='w', pady=2)
    
    def _create_permissions_field(self, parent):
        """创建权限设置字段"""
        # 标签
        label = ttk.Label(parent, text="权限设置", font=('Segoe UI', 10, 'bold'))
        label.pack(anchor='w', pady=(15, 5))
        
        # 权限列表
        permissions_frame = ttk.Frame(parent)
        permissions_frame.pack(fill='x', pady=(0, 5))
        
        # 定义权限选项
        permission_options = [
            ("用户管理", "user_management"),
            ("订单管理", "order_management"),
            ("库存管理", "inventory_management"),
            ("财务管理", "financial_management"),
            ("报表查看", "report_view"),
            ("系统设置", "system_settings"),
            ("数据导入导出", "data_import_export"),
            ("会员管理", "member_management")
        ]
        
        self.permission_vars = {}
        for text, value in permission_options:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(permissions_frame, text=text, variable=var)
            cb.pack(anchor='w', pady=2)
            self.permission_vars[value] = var
    
    def _populate_form(self):
        """填充表单数据"""
        if not self.user:
            return
            
        self.entries['username'].insert(0, self.user.username)
        self.entries['email'].insert(0, self.user.email)
        self.entries['phone'].insert(0, self.user.phone)
        self.entries['department'].insert(0, self.user.department)
        
        self.role_var.set(self.user.role)
        self.status_var.set(self.user.status)
        
        # 设置权限
        for perm, var in self.permission_vars.items():
            var.set(perm in self.user.permissions)
    
    def confirm(self):
        """确认提交"""
        try:
            # 验证必填字段
            username = self.entries['username'].get().strip()
            email = self.entries['email'].get().strip()
            
            if not username:
                messagebox.showerror("错误", "用户名不能为空")
                return
                
            if not email:
                messagebox.showerror("错误", "邮箱不能为空")
                return
            
            # 收集数据
            data = {
                'username': username,
                'email': email,
                'phone': self.entries['phone'].get().strip(),
                'department': self.entries['department'].get().strip(),
                'role': self.role_var.get(),
                'status': self.status_var.get()
            }
            
            # 如果是新建用户，添加密码
            if not self.user:
                password = self.entries['password'].get().strip()
                if not password:
                    messagebox.showerror("错误", "密码不能为空")
                    return
                data['password'] = password
            
            # 收集权限
            data['permissions'] = [perm for perm, var in self.permission_vars.items() if var.get()]
            
            self.result = data
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"表单提交失败: {e}")
    
    def cancel(self):
        """取消"""
        self.result = None
        self.root.destroy()


class PermissionManagementDialog(BaseDialog):
    """权限管理对话框"""
    
    def __init__(self, parent: tk.Widget, user: User):
        self.user = user
        self.result = None
        super().__init__("权限管理", parent, width=600, height=500)
    
    def create_widget(self):
        """创建权限管理界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 用户信息
        user_info_label = ttk.Label(
            main_frame, 
            text=f"用户: {self.user.username} ({self.user.email})",
            font=('Segoe UI', 12, 'bold')
        )
        user_info_label.pack(pady=(0, 20))
        
        # 权限树形控件
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.permission_tree = ttk.Treeview(tree_frame, show='tree headings')
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.permission_tree.yview)
        self.permission_tree.configure(yscrollcommand=scrollbar.set)
        
        # 配置列
        self.permission_tree.heading("#0", text="功能模块")
        self.permission_tree.heading("read", text="查看")
        self.permission_tree.heading("write", text="编辑")
        self.permission_tree.heading("delete", text="删除")
        self.permission_tree.heading("admin", text="管理")
        
        self.permission_tree.column("#0", width=200)
        self.permission_tree.column("read", width=80)
        self.permission_tree.column("write", width=80)
        self.permission_tree.column("delete", width=80)
        self.permission_tree.column("admin", width=80)
        
        # 权限数据
        self._create_permission_tree()
        
        # 布局
        self.permission_tree.pack(side="left", fill='both', expand=True)
        scrollbar.pack(side="right", fill='y')
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        # 确定按钮
        confirm_btn = ttk.Button(
            button_frame, 
            text="确定", 
            command=self.confirm,
            style='Accent.TButton'
        )
        confirm_btn.pack(side='right', padx=(10, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_btn.pack(side='right')
        
        # 权限说明
        info_label = ttk.Label(
            main_frame,
            text="提示：勾选相应权限，复选框表示拥有该权限",
            font=('Segoe UI', 8)
        )
        info_label.pack(anchor='w', pady=(10, 0))
    
    def _create_permission_tree(self):
        """创建权限树"""
        # 权限数据
        permissions_data = {
            "用户管理": {
                "view_users": {"read": True, "write": False, "delete": False, "admin": False},
                "edit_users": {"read": True, "write": True, "delete": False, "admin": False},
                "manage_users": {"read": True, "write": True, "delete": True, "admin": True}
            },
            "订单管理": {
                "view_orders": {"read": True, "write": False, "delete": False, "admin": False},
                "edit_orders": {"read": True, "write": True, "delete": False, "admin": False},
                "manage_orders": {"read": True, "write": True, "delete": True, "admin": True}
            },
            "库存管理": {
                "view_inventory": {"read": True, "write": False, "delete": False, "admin": False},
                "edit_inventory": {"read": True, "write": True, "delete": False, "admin": False},
                "manage_inventory": {"read": True, "write": True, "delete": True, "admin": True}
            },
            "财务管理": {
                "view_finance": {"read": True, "write": False, "delete": False, "admin": False},
                "edit_finance": {"read": True, "write": True, "delete": False, "admin": False},
                "manage_finance": {"read": True, "write": True, "delete": True, "admin": True}
            }
        }
        
        # 创建树形结构
        for module_name, module_permissions in permissions_data.items():
            # 插入模块
            module_id = self.permission_tree.insert("", "end", text=module_name, open=True)
            
            # 插入权限项
            for perm_name, perm_data in module_permissions.items():
                item_id = self.permission_tree.insert(
                    module_id, "end", 
                    text=perm_name.replace("_", " ").title(),
                    values=(perm_data["read"], perm_data["write"], perm_data["delete"], perm_data["admin"])
                )
                
                # 如果用户已有该权限，选中
                if perm_name in self.user.permissions:
                    # 这里应该根据实际的权限数据结构来设置
                    # 简化处理
                    self.permission_tree.item(item_id, tags=("selected",))
        
        # 配置复选框样式
        self.permission_tree.tag_configure("selected", background="lightblue")
    
    def confirm(self):
        """确认权限设置"""
        # 收集选中的权限
        selected_permissions = []
        
        def collect_permissions(parent=""):
            for item in self.permission_tree.get_children(parent):
                item_text = self.permission_tree.item(item, "text")
                if self.permission_tree.get_children(item):  # 有子项
                    collect_permissions(item)
                else:  # 叶子节点
                    # 检查是否选中
                    if item in self.permission_tree.selection():
                        selected_permissions.append(item_text.lower().replace(" ", "_"))
        
        collect_permissions()
        
        self.result = selected_permissions
        self.root.destroy()
    
    def cancel(self):
        """取消"""
        self.result = None
        self.root.destroy()


class ActivityLogDialog(BaseDialog):
    """活动日志对话框"""
    
    def __init__(self, parent: tk.Widget, user: User = None):
        self.user = user
        self.result = None
        super().__init__("活动日志" if not user else f"用户活动日志 - {user.username}", 
                        parent, width=800, height=600)
    
    def create_widget(self):
        """创建活动日志界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 筛选控件
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill='x', pady=(0, 15))
        
        # 日期范围
        ttk.Label(filter_frame, text="开始日期:").pack(side='left', padx=(0, 5))
        self.start_date = ttk.Entry(filter_frame, width=12)
        self.start_date.pack(side='left', padx=(0, 10))
        self.start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        
        ttk.Label(filter_frame, text="结束日期:").pack(side='left', padx=(0, 5))
        self.end_date = ttk.Entry(filter_frame, width=12)
        self.end_date.pack(side='left', padx=(0, 10))
        self.end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 搜索按钮
        search_btn = ttk.Button(filter_frame, text="搜索", command=self.search_logs)
        search_btn.pack(side='left', padx=(10, 0))
        
        # 操作按钮
        actions_frame = ttk.Frame(filter_frame)
        actions_frame.pack(side='right')
        
        export_btn = ttk.Button(actions_frame, text="导出日志", command=self.export_logs)
        export_btn.pack(side='right', padx=(5, 0))
        
        refresh_btn = ttk.Button(actions_frame, text="刷新", command=self.refresh_logs)
        refresh_btn.pack(side='right')
        
        # 日志表格
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill='both', expand=True)
        
        # 创建Treeview
        columns = ('时间', '用户', '操作', '详情', 'IP地址')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=15)
        
        # 配置列
        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)
        
        # 滚动条
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=log_scrollbar.set)
        
        # 布局
        self.log_tree.pack(side="left", fill='both', expand=True)
        log_scrollbar.pack(side="right", fill='y')
        
        # 加载日志数据
        self.load_logs()
        
        # 关闭按钮
        close_btn = ttk.Button(main_frame, text="关闭", command=self.close_dialog)
        close_btn.pack(pady=(15, 0))
    
    def load_logs(self):
        """加载日志数据"""
        # 清空现有数据
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # 模拟日志数据
        logs_data = [
            ActivityLog(1, 1, "登录", "用户成功登录系统", "2025-11-08 10:30:15", "192.168.1.100"),
            ActivityLog(2, 1, "修改资料", "更新了用户个人信息", "2025-11-08 09:15:20", "192.168.1.100"),
            ActivityLog(3, 1, "订单操作", "创建了新的销售订单", "2025-11-07 16:45:30", "192.168.1.100"),
            ActivityLog(4, 1, "权限变更", "用户权限被修改", "2025-11-07 14:20:10", "192.168.1.200"),
            ActivityLog(5, 2, "登录", "用户成功登录系统", "2025-11-08 11:00:00", "192.168.1.101")
        ]
        
        # 如果指定了用户，过滤日志
        if self.user:
            logs_data = [log for log in logs_data if log.user_id == self.user.user_id]
        
        # 插入日志数据
        for log in logs_data:
            username = f"用户{log.user_id}" if not self.user else self.user.username
            self.log_tree.insert('', 'end', values=(
                log.timestamp, username, log.action, log.details, log.ip_address
            ))
    
    def search_logs(self):
        """搜索日志"""
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        # 这里应该实现实际的搜索逻辑
        # 简化处理，只是重新加载
        self.load_logs()
        messagebox.showinfo("提示", f"已搜索 {start_date} 到 {end_date} 的日志")
    
    def refresh_logs(self):
        """刷新日志"""
        self.load_logs()
        messagebox.showinfo("提示", "日志已刷新")
    
    def export_logs(self):
        """导出日志"""
        messagebox.showinfo("提示", "日志导出功能开发中...")
    
    def close_dialog(self):
        """关闭对话框"""
        self.root.destroy()


class SecuritySettingsDialog(BaseDialog):
    """安全设置对话框"""
    
    def __init__(self, parent: tk.Widget):
        self.result = None
        super().__init__("安全设置", parent, width=600, height=500)
    
    def create_widget(self):
        """创建安全设置界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="系统安全设置",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # 密码策略选项卡
        self._create_password_policy_tab(notebook)
        
        # 登录安全选项卡
        self._create_login_security_tab(notebook)
        
        # 数据保护选项卡
        self._create_data_protection_tab(notebook)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        # 保存按钮
        save_btn = ttk.Button(
            button_frame, 
            text="保存设置", 
            command=self.save_settings,
            style='Accent.TButton'
        )
        save_btn.pack(side='right', padx=(10, 0))
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_btn.pack(side='right')
        
        # 重置按钮
        reset_btn = ttk.Button(button_frame, text="重置为默认", command=self.reset_to_default)
        reset_btn.pack(side='right', padx=(0, 10))
    
    def _create_password_policy_tab(self, notebook):
        """创建密码策略选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="密码策略")
        
        # 密码长度
        ttk.Label(tab, text="最小密码长度:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        length_frame = ttk.Frame(tab)
        length_frame.pack(fill='x', pady=(0, 15))
        
        self.min_length_var = tk.IntVar(value=8)
        length_spinbox = ttk.Spinbox(length_frame, from_=6, to=20, textvariable=self.min_length_var, width=10)
        length_spinbox.pack(side='left')
        ttk.Label(length_frame, text="字符").pack(side='left', padx=(10, 0))
        
        # 密码复杂度
        ttk.Label(tab, text="密码复杂度要求:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(15, 5))
        
        self.require_upper_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="必须包含大写字母", variable=self.require_upper_var).pack(anchor='w', pady=2)
        
        self.require_lower_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="必须包含小写字母", variable=self.require_lower_var).pack(anchor='w', pady=2)
        
        self.require_number_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="必须包含数字", variable=self.require_number_var).pack(anchor='w', pady=2)
        
        self.require_special_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text="必须包含特殊字符", variable=self.require_special_var).pack(anchor='w', pady=2)
        
        # 密码过期
        ttk.Label(tab, text="密码过期设置:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        password_expiry_frame = ttk.Frame(tab)
        password_expiry_frame.pack(fill='x', pady=(0, 15))
        
        self.password_expiry_var = tk.IntVar(value=90)
        expiry_spinbox = ttk.Spinbox(
            password_expiry_frame, from_=0, to=365, 
            textvariable=self.password_expiry_var, width=10
        )
        expiry_spinbox.pack(side='left')
        ttk.Label(password_expiry_frame, text="天后过期 (0表示永不过期)").pack(side='left', padx=(10, 0))
        
        # 密码历史
        history_frame = ttk.Frame(tab)
        history_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(history_frame, text="密码历史记录:").pack(side='left')
        self.password_history_var = tk.IntVar(value=5)
        history_spinbox = ttk.Spinbox(
            history_frame, from_=0, to=20, 
            textvariable=self.password_history_var, width=10
        )
        history_spinbox.pack(side='left', padx=(10, 0))
        ttk.Label(history_frame, text="次 (防止重复使用)").pack(side='left', padx=(10, 0))
    
    def _create_login_security_tab(self, notebook):
        """创建登录安全选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="登录安全")
        
        # 登录尝试限制
        ttk.Label(tab, text="登录尝试限制:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        attempt_frame = ttk.Frame(tab)
        attempt_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(attempt_frame, text="最大失败次数:").pack(side='left')
        self.max_attempts_var = tk.IntVar(value=5)
        attempt_spinbox = ttk.Spinbox(
            attempt_frame, from_=3, to=10, 
            textvariable=self.max_attempts_var, width=10
        )
        attempt_spinbox.pack(side='left', padx=(10, 0))
        
        lockout_frame = ttk.Frame(tab)
        lockout_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(lockout_frame, text="锁定时间:").pack(side='left')
        self.lockout_duration_var = tk.IntVar(value=15)
        lockout_spinbox = ttk.Spinbox(
            lockout_frame, from_=5, to=60, 
            textvariable=self.lockout_duration_var, width=10
        )
        lockout_spinbox.pack(side='left', padx=(10, 0))
        ttk.Label(lockout_frame, text="分钟").pack(side='left', padx=(10, 0))
        
        # 会话管理
        ttk.Label(tab, text="会话管理:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        self.session_timeout_var = tk.IntVar(value=30)
        timeout_frame = ttk.Frame(tab)
        timeout_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(timeout_frame, text="会话超时时间:").pack(side='left')
        timeout_spinbox = ttk.Spinbox(
            timeout_frame, from_=15, to=480, 
            textvariable=self.session_timeout_var, width=10
        )
        timeout_spinbox.pack(side='left', padx=(10, 0))
        ttk.Label(timeout_frame, text="分钟").pack(side='left', padx=(10, 0))
        
        self.force_logout_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab, 
            text="会话超时后强制登出", 
            variable=self.force_logout_var
        ).pack(anchor='w', pady=2)
        
        # 双因素认证
        ttk.Label(tab, text="双因素认证:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        self.enable_2fa_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            tab, 
            text="启用双因素认证", 
            variable=self.enable_2fa_var
        ).pack(anchor='w', pady=2)
        
        self.enforce_2fa_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            tab, 
            text="强制所有用户使用双因素认证", 
            variable=self.enforce_2fa_var
        ).pack(anchor='w', pady=2)
    
    def _create_data_protection_tab(self, notebook):
        """创建数据保护选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="数据保护")
        
        # 数据加密
        ttk.Label(tab, text="数据加密:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        self.encrypt_sensitive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab, 
            text="加密敏感数据", 
            variable=self.encrypt_sensitive_var
        ).pack(anchor='w', pady=2)
        
        self.encrypt_passwords_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab, 
            text="加密用户密码", 
            variable=self.encrypt_passwords_var
        ).pack(anchor='w', pady=2)
        
        # 数据备份
        ttk.Label(tab, text="数据备份:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab, 
            text="自动备份用户数据", 
            variable=self.auto_backup_var
        ).pack(anchor='w', pady=2)
        
        backup_freq_frame = ttk.Frame(tab)
        backup_freq_frame.pack(fill='x', pady=(5, 15))
        
        ttk.Label(backup_freq_frame, text="备份频率:").pack(side='left')
        self.backup_frequency_var = tk.StringVar(value="daily")
        backup_combo = ttk.Combobox(
            backup_freq_frame, 
            textvariable=self.backup_frequency_var,
            values=["daily", "weekly", "monthly"],
            state="readonly",
            width=15
        )
        backup_combo.pack(side='left', padx=(10, 0))
        
        # 访问日志
        ttk.Label(tab, text="访问日志:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20, 5))
        
        self.log_access_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab, 
            text="记录所有用户访问", 
            variable=self.log_access_var
        ).pack(anchor='w', pady=2)
        
        self.log_data_changes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            tab, 
            text="记录数据变更", 
            variable=self.log_data_changes_var
        ).pack(anchor='w', pady=2)
        
        retention_frame = ttk.Frame(tab)
        retention_frame.pack(fill='x', pady=(5, 15))
        
        ttk.Label(retention_frame, text="日志保留时间:").pack(side='left')
        self.log_retention_var = tk.IntVar(value=90)
        retention_spinbox = ttk.Spinbox(
            retention_frame, from_=30, to=365, 
            textvariable=self.log_retention_var, width=10
        )
        retention_spinbox.pack(side='left', padx=(10, 0))
        ttk.Label(retention_frame, text="天").pack(side='left', padx=(10, 0))
    
    def save_settings(self):
        """保存设置"""
        try:
            # 这里应该实现实际的保存逻辑
            # 收集所有设置值
            settings = {
                'password_policy': {
                    'min_length': self.min_length_var.get(),
                    'require_upper': self.require_upper_var.get(),
                    'require_lower': self.require_lower_var.get(),
                    'require_number': self.require_number_var.get(),
                    'require_special': self.require_special_var.get(),
                    'expiry_days': self.password_expiry_var.get(),
                    'history_count': self.password_history_var.get()
                },
                'login_security': {
                    'max_attempts': self.max_attempts_var.get(),
                    'lockout_duration': self.lockout_duration_var.get(),
                    'session_timeout': self.session_timeout_var.get(),
                    'force_logout': self.force_logout_var.get(),
                    'enable_2fa': self.enable_2fa_var.get(),
                    'enforce_2fa': self.enforce_2fa_var.get()
                },
                'data_protection': {
                    'encrypt_sensitive': self.encrypt_sensitive_var.get(),
                    'encrypt_passwords': self.encrypt_passwords_var.get(),
                    'auto_backup': self.auto_backup_var.get(),
                    'backup_frequency': self.backup_frequency_var.get(),
                    'log_access': self.log_access_var.get(),
                    'log_data_changes': self.log_data_changes_var.get(),
                    'log_retention': self.log_retention_var.get()
                }
            }
            
            # 保存到配置文件或数据库
            messagebox.showinfo("成功", "安全设置已保存")
            self.result = settings
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    
    def cancel(self):
        """取消"""
        self.result = None
        self.root.destroy()
    
    def reset_to_default(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            # 重置所有设置到默认值
            # 这里应该实现重置逻辑
            messagebox.showinfo("提示", "已重置为默认设置")


class UserManagementGUI(BaseFrame):
    """用户管理主界面"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        
        # 模拟用户数据
        self.users = [
            User(1, "admin", "admin@flowershop.com", "admin", "active", 
                 "2025-01-01 08:00:00", "2025-11-08 11:00:00",
                 ["user_management", "system_settings"], "13800138000", "信息技术部"),
            User(2, "manager", "manager@flowershop.com", "manager", "active",
                 "2025-01-15 09:00:00", "2025-11-08 10:30:00",
                 ["order_management", "report_view"], "13800138001", "销售部"),
            User(3, "accountant", "accountant@flowershop.com", "accountant", "active",
                 "2025-02-01 10:00:00", "2025-11-07 16:45:00",
                 ["financial_management", "report_view"], "13800138002", "财务部"),
            User(4, "sales001", "sales001@flowershop.com", "sales", "active",
                 "2025-03-01 11:00:00", "2025-11-08 09:15:00",
                 ["order_management", "member_management"], "13800138003", "销售部"),
            User(5, "disabled_user", "disabled@flowershop.com", "user", "disabled",
                 "2025-04-01 12:00:00", "2025-10-15 14:20:00",
                 ["order_management"], "13800138004", "客服部")
        ]
        
        self.current_user = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar()
    
    def create_widget(self):
        """创建用户管理界面"""
        # 主容器
        main_frame = ttk.Frame(self.widget)
        main_frame.pack(fill='both', expand=True)
        
        # 顶部工具栏
        self._create_toolbar(main_frame)
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # 用户管理选项卡
        self._create_user_management_tab(notebook)
        
        # 权限管理选项卡
        self._create_permission_management_tab(notebook)
        
        # 活动日志选项卡
        self._create_activity_log_tab(notebook)
        
        # 安全设置选项卡
        self._create_security_settings_tab(notebook)
    
    def _create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill='x', pady=(0, 10))
        
        # 标题
        title_label = ttk.Label(
            toolbar, 
            text="用户管理系统", 
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(side='left')
        
        # 搜索和筛选
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side='right')
        
        # 搜索框
        ttk.Label(search_frame, text="搜索:").pack(side='left', padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # 状态筛选
        ttk.Label(search_frame, text="状态:").pack(side='left', padx=(0, 5))
        status_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.filter_var,
            values=["全部", "活跃", "禁用", "待审核"],
            state="readonly",
            width=10
        )
        status_combo.pack(side='left', padx=(0, 10))
        status_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            search_frame, 
            text="刷新", 
            command=self.refresh_data
        )
        refresh_btn.pack(side='left')
    
    def _create_user_management_tab(self, notebook):
        """创建用户管理选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="用户管理")
        
        # 操作按钮组
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill='x', pady=(0, 10))
        
        # 创建用户按钮
        create_btn = ttk.Button(
            button_frame, 
            text="创建用户", 
            command=self.create_user,
            style='Accent.TButton'
        )
        create_btn.pack(side='left', padx=(0, 10))
        
        # 编辑用户按钮
        edit_btn = ttk.Button(
            button_frame, 
            text="编辑用户", 
            command=self.edit_user
        )
        edit_btn.pack(side='left', padx=(0, 10))
        
        # 删除用户按钮
        delete_btn = ttk.Button(
            button_frame, 
            text="删除用户", 
            command=self.delete_user
        )
        delete_btn.pack(side='left', padx=(0, 10))
        
        # 状态管理按钮
        status_btn = ttk.Button(
            button_frame, 
            text="状态管理", 
            command=self.manage_user_status
        )
        status_btn.pack(side='left', padx=(0, 10))
        
        # 权限管理按钮
        permission_btn = ttk.Button(
            button_frame, 
            text="权限管理", 
            command=self.manage_permissions
        )
        permission_btn.pack(side='left', padx=(0, 10))
        
        # 用户表格
        table_frame = ttk.Frame(tab)
        table_frame.pack(fill='both', expand=True)
        
        # 创建Treeview
        columns = ('ID', '用户名', '邮箱', '角色', '状态', '部门', '手机号', 
                  '创建时间', '最后登录', '权限数量')
        self.user_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 配置列
        column_widths = [50, 120, 180, 80, 80, 100, 120, 120, 120, 80]
        for i, col in enumerate(columns):
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=column_widths[i])
        
        # 滚动条
        user_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scrollbar.set)
        
        # 绑定选择事件
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        self.user_tree.bind('<Double-1>', self.on_user_double_click)
        
        # 布局
        self.user_tree.pack(side="left", fill='both', expand=True)
        user_scrollbar.pack(side="right", fill='y')
        
        # 底部信息栏
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill='x', pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, text="就绪", font=('Segoe UI', 9))
        self.info_label.pack(side='left')
        
        # 加载用户数据
        self.load_users()
    
    def _create_permission_management_tab(self, notebook):
        """创建权限管理选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="权限管理")
        
        # 权限概览
        overview_frame = ttk.LabelFrame(tab, text="权限概览", padding="10")
        overview_frame.pack(fill='x', pady=(0, 10))
        
        # 统计信息
        stats_frame = ttk.Frame(overview_frame)
        stats_frame.pack(fill='x')
        
        self._create_stat_card(stats_frame, "总用户数", len(self.users), 0)
        self._create_stat_card(stats_frame, "管理员", 
                              len([u for u in self.users if u.role == "admin"]), 1)
        self._create_stat_card(stats_frame, "活跃用户", 
                              len([u for u in self.users if u.status == "active"]), 2)
        self._create_stat_card(stats_frame, "待审核", 
                              len([u for u in self.users if u.status == "pending"]), 3)
        
        # 权限分配图表区域
        chart_frame = ttk.LabelFrame(tab, text="权限分配统计", padding="10")
        chart_frame.pack(fill='both', expand=True)
        
        # 这里可以添加权限统计图表
        # 简化处理，显示权限列表
        permission_list_frame = ttk.Frame(chart_frame)
        permission_list_frame.pack(fill='both', expand=True)
        
        # 权限统计表格
        perm_columns = ('权限名称', '拥有用户数', '描述')
        self.perm_tree = ttk.Treeview(permission_list_frame, columns=perm_columns, show='headings', height=10)
        
        for col in perm_columns:
            self.perm_tree.heading(col, text=col)
            self.perm_tree.column(col, width=200)
        
        # 权限统计数据
        permission_stats = [
            ("用户管理", 2, "管理用户账户和权限"),
            ("订单管理", 4, "查看和编辑订单信息"),
            ("库存管理", 1, "管理商品库存"),
            ("财务管理", 2, "财务数据管理"),
            ("报表查看", 3, "查看各类统计报表"),
            ("系统设置", 1, "系统配置管理"),
            ("会员管理", 2, "客户会员管理")
        ]
        
        for stat in permission_stats:
            self.perm_tree.insert('', 'end', values=stat)
        
        # 权限详情按钮
        detail_btn = ttk.Button(
            permission_list_frame, 
            text="查看权限详情", 
            command=self.show_permission_details
        )
        detail_btn.pack(pady=10)
        
        # 滚动条
        perm_scrollbar = ttk.Scrollbar(permission_list_frame, orient="vertical", command=self.perm_tree.yview)
        self.perm_tree.configure(yscrollcommand=perm_scrollbar.set)
        
        # 布局
        self.perm_tree.pack(side="left", fill='both', expand=True)
        perm_scrollbar.pack(side="right", fill='y')
    
    def _create_activity_log_tab(self, notebook):
        """创建活动日志选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="活动日志")
        
        # 日志控制面板
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # 时间范围选择
        ttk.Label(control_frame, text="时间范围:").pack(side='left', padx=(0, 5))
        
        time_combo = ttk.Combobox(
            control_frame, 
            values=["今天", "最近7天", "最近30天", "最近90天", "自定义"],
            state="readonly",
            width=15
        )
        time_combo.pack(side='left', padx=(0, 10))
        
        # 操作类型筛选
        ttk.Label(control_frame, text="操作类型:").pack(side='left', padx=(0, 5))
        
        action_combo = ttk.Combobox(
            control_frame, 
            values=["全部", "登录", "登出", "创建", "编辑", "删除", "权限变更"],
            state="readonly",
            width=15
        )
        action_combo.pack(side='left', padx=(0, 10))
        
        # 操作按钮
        log_buttons_frame = ttk.Frame(control_frame)
        log_buttons_frame.pack(side='right')
        
        view_all_btn = ttk.Button(
            log_buttons_frame, 
            text="查看所有日志", 
            command=self.view_all_logs
        )
        view_all_btn.pack(side='right', padx=(5, 0))
        
        export_btn = ttk.Button(
            log_buttons_frame, 
            text="导出日志", 
            command=self.export_logs
        )
        view_all_btn.pack(side='right', padx=(5, 0))
        
        # 日志表格
        log_frame = ttk.Frame(tab)
        log_frame.pack(fill='both', expand=True)
        
        # 创建Treeview
        log_columns = ('时间', '用户', '操作', '详情', 'IP地址', '状态')
        self.log_tree = ttk.Treeview(log_frame, columns=log_columns, show='headings', height=15)
        
        for col in log_columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)
        
        # 滚动条
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=log_scrollbar.set)
        
        # 布局
        self.log_tree.pack(side="left", fill='both', expand=True)
        log_scrollbar.pack(side="right", fill='y')
        
        # 加载日志数据
        self.load_activity_logs()
    
    def _create_security_settings_tab(self, notebook):
        """创建安全设置选项卡"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="安全设置")
        
        # 安全概览
        overview_frame = ttk.LabelFrame(tab, text="安全状态概览", padding="10")
        overview_frame.pack(fill='x', pady=(0, 10))
        
        # 安全状态卡片
        security_status_frame = ttk.Frame(overview_frame)
        security_status_frame.pack(fill='x')
        
        self._create_security_card(security_status_frame, "密码策略", "已启用", True, 0)
        self._create_security_card(security_status_frame, "登录限制", "5次失败锁定", True, 1)
        self._create_security_card(security_status_frame, "会话管理", "30分钟超时", True, 2)
        self._create_security_card(security_status_frame, "双因素认证", "未启用", False, 3)
        
        # 快速设置
        quick_settings_frame = ttk.LabelFrame(tab, text="快速设置", padding="10")
        quick_settings_frame.pack(fill='x', pady=(0, 10))
        
        settings_buttons_frame = ttk.Frame(quick_settings_frame)
        settings_buttons_frame.pack(fill='x')
        
        # 密码策略设置
        password_btn = ttk.Button(
            settings_buttons_frame, 
            text="密码策略", 
            command=self.open_password_policy
        )
        password_btn.pack(side='left', padx=(0, 10))
        
        # 登录安全设置
        login_btn = ttk.Button(
            settings_buttons_frame, 
            text="登录安全", 
            command=self.open_login_security
        )
        login_btn.pack(side='left', padx=(0, 10))
        
        # 数据保护设置
        data_btn = ttk.Button(
            settings_buttons_frame, 
            text="数据保护", 
            command=self.open_data_protection
        )
        data_btn.pack(side='left', padx=(0, 10))
        
        # 高级安全设置
        advanced_btn = ttk.Button(
            settings_buttons_frame, 
            text="高级设置", 
            command=self.open_security_settings
        )
        advanced_btn.pack(side='left')
        
        # 安全日志
        log_frame = ttk.LabelFrame(tab, text="最近安全事件", padding="10")
        log_frame.pack(fill='both', expand=True)
        
        # 安全事件表格
        security_columns = ('时间', '事件类型', '用户', 'IP地址', '状态', '描述')
        self.security_tree = ttk.Treeview(log_frame, columns=security_columns, show='headings', height=10)
        
        for col in security_columns:
            self.security_tree.heading(col, text=col)
            self.security_tree.column(col, width=150)
        
        # 安全事件数据
        security_events = [
            ("2025-11-08 10:30:15", "登录成功", "admin", "192.168.1.100", "正常", "用户正常登录"),
            ("2025-11-08 09:45:22", "密码错误", "unknown", "192.168.1.200", "警告", "3次密码错误尝试"),
            ("2025-11-08 08:15:30", "权限变更", "admin", "192.168.1.100", "正常", "用户权限被修改"),
            ("2025-11-07 16:20:45", "异常登录", "manager", "192.168.1.150", "警告", "异地登录检测")
        ]
        
        for event in security_events:
            self.security_tree.insert('', 'end', values=event)
        
        # 滚动条
        security_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.security_tree.yview)
        self.security_tree.configure(yscrollcommand=security_scrollbar.set)
        
        # 布局
        self.security_tree.pack(side="left", fill='both', expand=True)
        security_scrollbar.pack(side="right", fill='y')
    
    def _create_stat_card(self, parent, title: str, value: int, index: int):
        """创建统计卡片"""
        card_frame = ttk.Frame(parent)
        card_frame.pack(side='left', padx=(0, 20), fill='both', expand=True)
        
        # 卡片背景
        card = ttk.Frame(card_frame, relief='raised', borderwidth=1)
        card.pack(fill='both', expand=True, pady=2)
        
        # 标题
        title_label = ttk.Label(card, text=title, font=('Segoe UI', 10))
        title_label.pack(pady=(10, 5))
        
        # 数值
        value_label = ttk.Label(card, text=str(value), font=('Segoe UI', 16, 'bold'))
        value_label.pack(pady=(0, 10))
    
    def _create_security_card(self, parent, title: str, description: str, is_secure: bool, index: int):
        """创建安全状态卡片"""
        card_frame = ttk.Frame(parent)
        card_frame.pack(side='left', padx=(0, 20), fill='both', expand=True)
        
        # 卡片背景
        card = ttk.Frame(card_frame, relief='raised', borderwidth=1)
        card.pack(fill='both', expand=True, pady=2)
        
        # 状态指示器
        status_color = "green" if is_secure else "red"
        status_label = ttk.Label(card, text="●", foreground=status_color, font=('Segoe UI', 16))
        status_label.pack(pady=(10, 5))
        
        # 标题
        title_label = ttk.Label(card, text=title, font=('Segoe UI', 10, 'bold'))
        title_label.pack(pady=(0, 5))
        
        # 描述
        desc_label = ttk.Label(card, text=description, font=('Segoe UI', 9))
        desc_label.pack(pady=(0, 10))
    
    def load_users(self):
        """加载用户数据"""
        # 清空现有数据
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # 插入用户数据
        for user in self.users:
            self.user_tree.insert('', 'end', values=(
                user.user_id, user.username, user.email, user.role,
                self._get_status_text(user.status), user.department,
                user.phone, user.created_at, user.last_login or "从未登录",
                len(user.permissions)
            ))
        
        # 更新状态信息
        total_users = len(self.users)
        active_users = len([u for u in self.users if u.status == "active"])
        self.info_label.config(text=f"共 {total_users} 个用户，{active_users} 个活跃用户")
    
    def _get_status_text(self, status: str) -> str:
        """获取状态显示文本"""
        status_map = {
            "active": "活跃",
            "disabled": "禁用",
            "pending": "待审核"
        }
        return status_map.get(status, status)
    
    def load_activity_logs(self):
        """加载活动日志数据"""
        # 清空现有数据
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # 模拟日志数据
        logs_data = [
            ("2025-11-08 11:00:00", "admin", "登录", "用户成功登录系统", "192.168.1.100", "成功"),
            ("2025-11-08 10:45:15", "manager", "编辑", "修改了用户权限", "192.168.1.101", "成功"),
            ("2025-11-08 10:30:22", "sales001", "创建", "创建了新的销售订单", "192.168.1.102", "成功"),
            ("2025-11-08 09:15:30", "accountant", "查看", "查看了财务报表", "192.168.1.103", "成功"),
            ("2025-11-07 16:45:12", "admin", "删除", "删除了用户账户", "192.168.1.100", "成功"),
            ("2025-11-07 14:20:05", "unknown", "登录", "密码错误登录尝试", "192.168.1.200", "失败")
        ]
        
        for log in logs_data:
            self.log_tree.insert('', 'end', values=log)
    
    def on_user_select(self, event):
        """用户选择事件"""
        selection = self.user_tree.selection()
        if selection:
            item = selection[0]
            user_id = self.user_tree.item(item, 'values')[0]
            # 查找用户
            self.current_user = next((u for u in self.users if u.user_id == int(user_id)), None)
            self.info_label.config(text=f"已选择用户: {self.current_user.username}")
        else:
            self.current_user = None
            self.info_label.config(text="就绪")
    
    def on_user_double_click(self, event):
        """用户双击事件"""
        if self.current_user:
            self.edit_user()
    
    def on_search(self, event):
        """搜索事件"""
        search_text = self.search_var.get().lower()
        if not search_text:
            self.load_users()
            return
        
        # 筛选用户
        filtered_users = []
        for user in self.users:
            if (search_text in user.username.lower() or 
                search_text in user.email.lower() or
                search_text in user.phone.lower()):
                filtered_users.append(user)
        
        # 清空并重新加载
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        for user in filtered_users:
            self.user_tree.insert('', 'end', values=(
                user.user_id, user.username, user.email, user.role,
                self._get_status_text(user.status), user.department,
                user.phone, user.created_at, user.last_login or "从未登录",
                len(user.permissions)
            ))
    
    def on_filter_change(self, event):
        """筛选变更事件"""
        filter_text = self.filter_var.get()
        if filter_text == "全部":
            self.load_users()
            return
        
        # 状态映射
        status_map = {
            "活跃": "active",
            "禁用": "disabled", 
            "待审核": "pending"
        }
        
        filter_status = status_map.get(filter_text)
        if not filter_status:
            return
        
        # 筛选用户
        filtered_users = [u for u in self.users if u.status == filter_status]
        
        # 清空并重新加载
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        for user in filtered_users:
            self.user_tree.insert('', 'end', values=(
                user.user_id, user.username, user.email, user.role,
                self._get_status_text(user.status), user.department,
                user.phone, user.created_at, user.last_login or "从未登录",
                len(user.permissions)
            ))
    
    def create_user(self):
        """创建用户"""
        dialog = UserFormDialog(self.widget, None)
        result = dialog.show()
        
        if result:
            try:
                # 创建新用户
                new_user = User(
                    user_id=len(self.users) + 1,
                    username=result['username'],
                    email=result['email'],
                    role=result['role'],
                    status=result['status'],
                    permissions=result['permissions'],
                    phone=result['phone'],
                    department=result['department']
                )
                
                self.users.append(new_user)
                self.load_users()
                messagebox.showinfo("成功", f"用户 {new_user.username} 创建成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"创建用户失败: {e}")
    
    def edit_user(self):
        """编辑用户"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择要编辑的用户")
            return
        
        dialog = UserFormDialog(self.widget, self.current_user)
        result = dialog.show()
        
        if result:
            try:
                # 更新用户信息
                self.current_user.username = result['username']
                self.current_user.email = result['email']
                self.current_user.role = result['role']
                self.current_user.status = result['status']
                self.current_user.permissions = result['permissions']
                self.current_user.phone = result['phone']
                self.current_user.department = result['department']
                
                self.load_users()
                messagebox.showinfo("成功", f"用户 {self.current_user.username} 更新成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"更新用户失败: {e}")
    
    def delete_user(self):
        """删除用户"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择要删除的用户")
            return
        
        if self.current_user.role == "admin":
            messagebox.showerror("错误", "不能删除管理员账户")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除用户 '{self.current_user.username}' 吗？"):
            try:
                self.users.remove(self.current_user)
                self.current_user = None
                self.load_users()
                messagebox.showinfo("成功", "用户删除成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"删除用户失败: {e}")
    
    def manage_user_status(self):
        """管理用户状态"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择要管理的用户")
            return
        
        # 状态管理对话框
        status_window = tk.Toplevel(self.widget)
        status_window.title(f"状态管理 - {self.current_user.username}")
        status_window.geometry("400x300")
        status_window.resizable(False, False)
        status_window.transient(self.widget)
        status_window.grab_set()
        
        # 状态管理界面
        main_frame = ttk.Frame(status_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # 用户信息
        user_info = ttk.Label(
            main_frame, 
            text=f"用户: {self.current_user.username}\n邮箱: {self.current_user.email}",
            font=('Segoe UI', 10)
        )
        user_info.pack(pady=(0, 20))
        
        # 当前状态
        ttk.Label(main_frame, text="当前状态:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        current_status_label = ttk.Label(
            main_frame, 
            text=self._get_status_text(self.current_user.status),
            font=('Segoe UI', 12)
        )
        current_status_label.pack(anchor='w', pady=(5, 15))
        
        # 新状态选择
        ttk.Label(main_frame, text="更改为:", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        status_var = tk.StringVar(value=self.current_user.status)
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=(5, 20))
        
        statuses = [("活跃", "active"), ("禁用", "disabled"), ("待审核", "pending")]
        for text, value in statuses:
            rb = ttk.Radiobutton(status_frame, text=text, variable=status_var, value=value)
            rb.pack(anchor='w', pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        def update_status():
            new_status = status_var.get()
            if new_status != self.current_user.status:
                self.current_user.status = new_status
                self.load_users()
                messagebox.showinfo("成功", "用户状态已更新")
            status_window.destroy()
        
        def reset_password():
            if messagebox.askyesno("确认", "确定要重置此用户的密码吗？"):
                messagebox.showinfo("提示", "密码重置邮件已发送")
                status_window.destroy()
        
        update_btn = ttk.Button(button_frame, text="更新状态", command=update_status, style='Accent.TButton')
        update_btn.pack(side='right', padx=(10, 0))
        
        reset_btn = ttk.Button(button_frame, text="重置密码", command=reset_password)
        reset_btn.pack(side='right')
        
        cancel_btn = ttk.Button(button_frame, text="取消", command=status_window.destroy)
        cancel_btn.pack(side='right', padx=(0, 10))
    
    def manage_permissions(self):
        """管理权限"""
        if not self.current_user:
            messagebox.showwarning("警告", "请先选择要管理权限的用户")
            return
        
        dialog = PermissionManagementDialog(self.widget, self.current_user)
        result = dialog.show()
        
        if result is not None:
            try:
                self.current_user.permissions = result
                self.load_users()
                messagebox.showinfo("成功", f"用户 {self.current_user.username} 权限已更新")
                
            except Exception as e:
                messagebox.showerror("错误", f"更新权限失败: {e}")
    
    def show_permission_details(self):
        """显示权限详情"""
        messagebox.showinfo("权限详情", "权限详细管理功能开发中...")
    
    def view_all_logs(self):
        """查看所有日志"""
        dialog = ActivityLogDialog(self.widget)
        dialog.show()
    
    def export_logs(self):
        """导出日志"""
        messagebox.showinfo("提示", "日志导出功能开发中...")
    
    def open_password_policy(self):
        """打开密码策略"""
        messagebox.showinfo("提示", "密码策略设置功能开发中...")
    
    def open_login_security(self):
        """打开登录安全"""
        messagebox.showinfo("提示", "登录安全设置功能开发中...")
    
    def open_data_protection(self):
        """打开数据保护"""
        messagebox.showinfo("提示", "数据保护设置功能开发中...")
    
    def open_security_settings(self):
        """打开安全设置"""
        dialog = SecuritySettingsDialog(self.widget)
        result = dialog.show()
        if result:
            messagebox.showinfo("成功", "安全设置已更新")
    
    def refresh_data(self):
        """刷新数据"""
        self.load_users()
        self.load_activity_logs()
        self.info_label.config(text="数据已刷新")
        self.search_var.set("")
        self.filter_var.set("全部")


def create_user_management_window():
    """创建用户管理窗口"""
    root = tk.Tk()
    root.title("用户管理系统 - Sister's Flower System")
    root.geometry("1200x800")
    
    # 应用Win11主题
    win11_theme.apply_theme(root)
    
    # 创建用户管理界面
    user_management = UserManagementGUI(root)
    user_management.initialize()
    user_management.show()
    
    return root


if __name__ == "__main__":
    # 创建并运行用户管理窗口
    app = create_user_management_window()
    app.mainloop()