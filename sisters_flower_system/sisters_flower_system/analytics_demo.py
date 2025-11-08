#!/usr/bin/env python3
"""
数据分析图表模块演示脚本
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.analytics_charts_gui import create_analytics_demo


def main():
    """主演示函数"""
    print("=" * 50)
    print("数据分析图表模块演示")
    print("=" * 50)
    print("功能特点:")
    print("✓ 销售趋势图表（折线图、柱状图）")
    print("✓ 商品销售占比（饼状图、环形图）")
    print("✓ 客户分析图表")
    print("✓ 库存分析图表")
    print("✓ 财务报表图表")
    print("✓ 实时数据更新")
    print("✓ 交互式图表功能")
    print("✓ 导出和打印功能")
    print("=" * 50)
    
    try:
        # 创建并运行演示
        demo = create_analytics_demo()
        print("正在启动数据分析图表系统...")
        demo.mainloop()
        
    except Exception as e:
        print(f"运行演示时出错: {e}")
        print("请确保所有依赖包都已正确安装")

if __name__ == "__main__":
    main()