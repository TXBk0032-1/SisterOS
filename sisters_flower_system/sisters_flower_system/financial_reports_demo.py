"""
财务报表模块演示程序
"""

import tkinter as tk
from gui.financial_reports_gui import FinancialReportsGUI
from config.win11_theme import win11_theme


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    root.title("姐妹花店 - 财务报表系统")
    root.geometry("1400x900")
    
    # 应用Win11主题
    win11_theme.set_theme('light')
    win11_theme.apply_theme(root)
    
    # 创建财务报表界面
    financial_reports = FinancialReportsGUI(root)
    financial_reports.pack(fill='both', expand=True)
    
    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()