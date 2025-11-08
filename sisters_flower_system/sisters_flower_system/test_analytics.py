#!/usr/bin/env python3
"""
数据分析图表模块测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chart_manager():
    """测试图表管理器"""
    try:
        from gui.analytics_charts_gui import ChartManager
        
        print("测试图表管理器...")
        manager = ChartManager()
        
        # 测试获取销售数据
        sales_data = manager.get_sales_data(7)
        print(f"✓ 销售数据: {len(sales_data['dates'])}天数据")
        
        # 测试获取商品销售数据
        product_data = manager.get_product_sales_data(5)
        print(f"✓ 商品数据: {len(product_data['products'])}种商品")
        
        # 测试获取客户数据
        customer_data = manager.get_customer_data()
        print(f"✓ 客户数据: {len(customer_data['types'])}种类型")
        
        # 测试获取库存数据
        inventory_data = manager.get_inventory_data()
        print(f"✓ 库存数据: {len(inventory_data['products'])}种商品")
        
        # 测试获取财务数据
        financial_data = manager.get_financial_data(6)
        print(f"✓ 财务数据: {len(financial_data['months'])}个月数据")
        
        print("图表管理器测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 图表管理器测试失败: {e}")
        return False

def test_imports():
    """测试模块导入"""
    try:
        print("测试模块导入...")
        import matplotlib.pyplot as plt
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        print("✓ 基础依赖包导入成功")
        
        from gui.analytics_charts_gui import ChartManager, AnalyticsChartsGUI, DataAnalyticsPanel
        print("✓ 自定义模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_gui_creation():
    """测试GUI创建"""
    try:
        print("测试GUI创建...")
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 创建数据分析面板
        from gui.analytics_charts_gui import DataAnalyticsPanel
        panel = DataAnalyticsPanel(root)
        print("✓ 数据分析面板创建成功")
        
        # 创建图表管理器
        from gui.analytics_charts_gui import ChartManager
        manager = ChartManager()
        print("✓ 图表管理器创建成功")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI创建测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("数据分析图表模块 - 功能测试")
    print("=" * 60)
    
    tests = [
        ("模块导入测试", test_imports),
        ("图表管理器测试", test_chart_manager),
        ("GUI创建测试", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n运行 {test_name}...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} - 通过")
        else:
            print(f"✗ {test_name} - 失败")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！数据分析图表模块可以正常使用。")
        print("\n使用方法:")
        print("  python analytics_demo.py          # 启动完整演示")
        print("  python -c 'from gui.analytics_charts_gui import *; create_analytics_demo().mainloop()'")
    else:
        print("❌ 部分测试失败，请检查依赖包和模块配置。")
    
    print("=" * 60)

if __name__ == "__main__":
    main()