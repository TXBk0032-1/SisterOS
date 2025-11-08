"""
GUI工具函数
提供界面相关的工具函数
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Tuple

from PIL import Image

# 导入设置，处理相对导入问题
try:
    from ..config.settings import SCALE_FACTOR
except ImportError:
    # 直接导入，处理相对导入问题
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import SCALE_FACTOR


def configure_scaling_and_font(root):
    """统一设置缩放和全局字体"""
    root.tk.call('tk', 'scaling', SCALE_FACTOR)
    base_font = font.nametofont("TkDefaultFont")
    base_font.configure(family="Microsoft YaHei", size=int(10 * SCALE_FACTOR))
    style = ttk.Style()
    style.configure('.', font=(base_font.actual('family'), base_font.actual('size')))
    style.configure('Treeview', rowheight=int(24 * SCALE_FACTOR))


def make_table(parent, cols) -> Tuple[ttk.Treeview, tk.Frame]:
    """创建带滚动条的 Treeview，行高自动适配缩放"""
    container = tk.Frame(parent)
    vsb = ttk.Scrollbar(container, orient="vertical")
    vsb.pack(side='right', fill='y')
    hsb = ttk.Scrollbar(container, orient="horizontal")
    hsb.pack(side='bottom', fill='x')

    tree = ttk.Treeview(
        container,
        columns=cols,
        show='headings',
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    tree.pack(fill='both', expand=True)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=int(100 * SCALE_FACTOR))
    return tree, container


def button_animation(button):
    """按钮点击动画：短暂变色+轻微抖动"""
    original_style = button.cget("style")
    original_pos = button.place_info() or button.grid_info()  # 兼容不同布局

    # 临时变色
    button.config(style="success.TButton")

    # 轻微抖动效果
    def shake(offset=2):
        if button.winfo_exists():  # 检查按钮是否仍存在
            if 'row' in original_pos:  # grid布局
                button.grid(row=original_pos['row'],
                            column=original_pos['column'],
                            padx=original_pos.get('padx', 0) + offset)
            elif 'x' in original_pos:  # place布局
                button.place(x=int(original_pos['x']) + offset,
                             y=original_pos['y'])
            button.after(50, lambda: shake(-offset) if offset != 0 else reset)

    def reset():
        if button.winfo_exists():
            button.config(style=original_style)
            if 'row' in original_pos:  # 恢复grid布局
                button.grid(row=original_pos['row'],
                            column=original_pos['column'],
                            padx=original_pos.get('padx', 0))
            elif 'x' in original_pos:  # 恢复place布局
                button.place(x=original_pos['x'], y=original_pos['y'])
            # 显示确认提示
            show_temp_message(button, "已确认！")

    shake()


def show_temp_message(widget, text, duration=1000):
    """在控件旁显示临时消息"""
    msg_window = tk.Toplevel(widget)
    msg_window.overrideredirect(True)  # 无边框
    msg_window.attributes("-topmost", True)

    # 计算显示位置（控件右下方）
    x = widget.winfo_rootx() + widget.winfo_width() + 10
    y = widget.winfo_rooty() + widget.winfo_height() // 2

    msg_window.geometry(f"+{x}+{y}")
    ttk.Label(msg_window, text=text, style="info.TLabel").pack(padx=5, pady=2)

    # 自动关闭
    def close_msg():
        if msg_window.winfo_exists():
            msg_window.destroy()

    msg_window.after(duration, close_msg)


def scale_image_to_fit(img, max_width=800, max_height=600):
    """将图片按比例缩放到最大宽高范围内"""
    width, height = img.size
    scale = min(max_width / width, max_height / height, 1.0)  # 不放大只缩小
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return img


def safe_open_image(image_path):
    """安全打开图片并返回副本，确保文件正确关闭"""
    with Image.open(image_path) as img:
        return img.copy()  # 返回副本避免文件句柄占用
