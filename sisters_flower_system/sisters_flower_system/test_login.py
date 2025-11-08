#!/usr/bin/env python3
"""
测试登录功能和主系统集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_sales_system import LoginWindow, EnhancedSalesSystem

def test_login_window():
    """测试登录窗口"""
    print("🧪 测试登录窗口...")
    
    try:
        # 创建登录窗口实例
        login_win = LoginWindow()
        print("✅ 登录窗口创建成功")
        
        # 测试run方法返回类型
        result = login_win.run()
        print(f"登录结果: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 登录窗口测试失败: {e}")
        return None, None

def test_main_system(user_info):
    """测试主系统"""
    print("🧪 测试主系统...")
    
    try:
        if user_info:
            # 创建主系统实例
            app = EnhancedSalesSystem(user_info)
            print("✅ 主系统创建成功")
            print(f"当前用户: {user_info}")
            
            # 测试display_user_info方法
            app.display_user_info()
            print("✅ 用户信息显示正常")
            
            return app
        else:
            print("⚠️ 无用户信息，跳过主系统测试")
            return None
            
    except Exception as e:
        print(f"❌ 主系统测试失败: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始测试登录和主系统集成")
    print("=" * 50)
    
    try:
        # 测试1: 登录窗口
        login_success, current_user = test_login_window()
        
        print("\n" + "=" * 50)
        
        # 测试2: 主系统
        if login_success:
            app = test_main_system(current_user)
            if app:
                print("✅ 所有测试通过！")
                print("\n💡 现在可以运行完整系统:")
                print("   python enhanced_sales_system.py")
            else:
                print("⚠️ 主系统测试未完成")
        else:
            print("❌ 登录失败，跳过主系统测试")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断测试")
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")

if __name__ == "__main__":
    main()