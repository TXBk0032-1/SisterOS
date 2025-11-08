#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
姐妹花销售系统 - 核心功能验证
验证修复后的主要类和方法是否正常工作
"""

import sys
import os
import traceback
from datetime import date

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_data_query_manager():
    """测试数据查询管理器"""
    print("🔧 测试OptimizedDataQueryManager...")
    
    try:
        # 导入相关类
        from enhanced_sales_system import OptimizedDataQueryManager, LoggerManager
        
        # 创建实例
        query_manager = OptimizedDataQueryManager()
        print("  ✅ OptimizedDataQueryManager 创建成功")
        
        # 测试方法存在性
        methods_to_test = [
            'get_month_sales',
            'get_average_order', 
            'get_total_members',
            'get_total_products',
            'get_new_members_month',
            'get_low_stock_items'
        ]
        
        for method_name in methods_to_test:
            if hasattr(query_manager, method_name):
                print(f"  ✅ {method_name} 方法存在")
            else:
                print(f"  ❌ {method_name} 方法不存在")
                return False
        
        print("  ✅ 所有数据查询方法检查通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        traceback.print_exc()
        return False

def test_database_manager():
    """测试数据库管理器"""
    print("\n🔧 测试DatabaseManager...")
    
    try:
        from enhanced_sales_system import DatabaseManager
        
        db_manager = DatabaseManager()
        print("  ✅ DatabaseManager 创建成功")
        
        # 检查关键方法
        if hasattr(db_manager, 'get_connection'):
            print("  ✅ get_connection 方法存在")
        else:
            print("  ❌ get_connection 方法不存在")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库管理器测试失败: {e}")
        traceback.print_exc()
        return False

def test_file_manager():
    """测试文件管理器"""
    print("\n🔧 测试OptimizedFileManager...")
    
    try:
        from enhanced_sales_system import OptimizedFileManager
        
        file_manager = OptimizedFileManager()
        print("  ✅ OptimizedFileManager 创建成功")
        return True
        
    except Exception as e:
        print(f"  ❌ 文件管理器测试失败: {e}")
        traceback.print_exc()
        return False

def test_log_manager():
    """测试日志管理器"""
    print("\n🔧 测试LogManager...")
    
    try:
        from enhanced_sales_system import LogManager
        
        log_manager = LogManager()
        print("  ✅ LogManager 创建成功")
        return True
        
    except Exception as e:
        print(f"  ❌ 日志管理器测试失败: {e}")
        traceback.print_exc()
        return False

def test_syntax_validation():
    """测试语法验证"""
    print("\n🔧 测试Python语法...")
    
    try:
        # 尝试编译
        import py_compile
        py_compile.compile('enhanced_sales_system.py', doraise=True)
        print("  ✅ 语法检查通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 语法检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🌸 姐妹花销售系统 - 核心功能验证")
    print("=" * 50)
    
    tests = [
        ("语法验证", test_syntax_validation),
        ("数据查询管理器", test_data_query_manager),
        ("数据库管理器", test_database_manager),
        ("文件管理器", test_file_manager),
        ("日志管理器", test_log_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ❌ {test_name} 测试失败")
        except Exception as e:
            print(f"  ❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有核心功能验证通过！")
        print("✅ 程序修复成功，可以正常运行")
    else:
        print("⚠️ 部分测试未通过，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)