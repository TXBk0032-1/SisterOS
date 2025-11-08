#!/usr/bin/env python3
"""
财务报表模块演示脚本
展示财务报表系统的各项功能
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.financial_reports_gui import FinancialReportsGUI, create_demo_window
from config.win11_theme import win11_theme


def create_main_demo():
    """创建主演示窗口"""
    # 创建主窗口
    root = tk.Tk()
    root.title("姐妹花店财务报表系统 - 完整演示")
    root.geometry("1400x900")
    
    # 应用Win11主题
    win11_theme.apply_theme(root)
    
    # 创建标题
    title_frame = ttk.Frame(root)
    title_frame.pack(fill='x', padx=20, pady=20)
    
    title_label = ttk.Label(
        title_frame,
        text="📊 姐妹花店财务报表系统",
        font=('Segoe UI', 18, 'bold'),
        foreground=win11_theme.colors['primary']
    )
    title_label.pack()
    
    subtitle_label = ttk.Label(
        title_frame,
        text="现代化财务管理解决方案",
        font=('Segoe UI', 10),
        foreground=win11_theme.colors['text_secondary']
    )
    subtitle_label.pack()
    
    # 创建财务报表界面
    financial_reports = FinancialReportsGUI(root)
    financial_reports.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    # 添加状态栏
    status_frame = ttk.Frame(root)
    status_frame.pack(fill='x', side='bottom')
    
    status_label = ttk.Label(
        status_frame,
        text="✅ 财务报表系统已启动 - 支持收入/支出分析、利润计算、现金流追踪、税务管理",
        font=('Segoe UI', 8),
        foreground=win11_theme.colors['text_secondary']
    )
    status_label.pack(pady=5)
    
    return root


def main():
    """主函数"""
    print("=" * 60)
    print("📊 姐妹花店财务报表系统演示")
    print("=" * 60)
    print()
    print("功能特性:")
    print("✅ 收入/支出明细报表")
    print("✅ 利润损失分析")
    print("✅ 现金流报表")
    print("✅ 税务报告功能")
    print("✅ 打印和导出功能")
    print("✅ 周期性报表生成")
    print("✅ 同比/环比分析")
    print("✅ 现代化Win11 UI设计")
    print("✅ 图表和数据分析")
    print()
    print("正在启动GUI界面...")
    print()
    
    # 创建并运行演示
    try:
        root = create_main_demo()
        root.mainloop()
    except Exception as e:
        print(f"启动失败: {e}")
        print("正在尝试使用简化演示...")
        try:
            demo = create_demo_window()
            demo.mainloop()
        except Exception as e2:
            print(f"简化演示也失败: {e2}")
            print("请检查依赖项是否正确安装")


if __name__ == "__main__":
    main()