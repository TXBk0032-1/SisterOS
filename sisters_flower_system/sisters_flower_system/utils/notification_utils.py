"""
通知工具模块
提供系统通知相关的功能
"""

import sys
import tkinter as tk
from typing import Optional
import time


class WindowsNotification:
    """Windows系统通知类"""
    
    def __init__(self):
        self.is_windows = sys.platform.startswith('win')
    
    def show_notification(self, title: str, message: str, duration: int = 3000) -> bool:
        """
        显示系统通知
        """
        if self.is_windows:
            try:
                # 尝试使用win10toast库
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    title,
                    message,
                    duration=duration // 1000,
                    threaded=True
                )
                return True
            except ImportError:
                # 如果没有win10toast库，使用fallback方法
                return self._fallback_notification(title, message, duration)
        else:
            return self._fallback_notification(title, message, duration)
    
    def _fallback_notification(self, title: str, message: str, duration: int) -> bool:
        """
        Fallback通知方法（使用tkinter）
        """
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 创建通知窗口
            notification = tk.Toplevel(root)
            notification.title("通知")
            notification.geometry("300x120")
            notification.resizable(False, False)
            notification.configure(bg='white')
            
            # 居中显示
            notification.update_idletasks()
            x = (notification.winfo_screenwidth() // 2) - (300 // 2)
            y = (notification.winfo_screenheight() // 2) - (120 // 2)
            notification.geometry(f"300x120+{x}+{y}")
            
            # 设置窗口置顶
            notification.attributes('-topmost', True)
            
            # 标题
            title_label = tk.Label(
                notification,
                text=title,
                font=('Segoe UI', 10, 'bold'),
                bg='white',
                fg='black'
            )
            title_label.pack(pady=(10, 5))
            
            # 消息
            message_label = tk.Label(
                notification,
                text=message,
                font=('Segoe UI', 9),
                bg='white',
                fg='gray',
                wraplength=280
            )
            message_label.pack(pady=5)
            
            # 确定按钮
            ok_button = tk.Button(
                notification,
                text="确定",
                command=notification.destroy,
                bg='blue',
                fg='white',
                relief='flat',
                padx=20
            )
            ok_button.pack(pady=10)
            
            # 自动关闭
            def auto_close():
                time.sleep(duration / 1000)
                try:
                    notification.destroy()
                    root.destroy()
                except:
                    pass
            
            import threading
            threading.Thread(target=auto_close, daemon=True).start()
            
            # 启动通知
            root.mainloop()
            return True
            
        except Exception as e:
            print(f"通知显示失败: {e}")
            return False
    
    def show_info(self, title: str, message: str, duration: int = 3000) -> bool:
        """显示信息通知"""
        return self.show_notification(f"ℹ️ {title}", message, duration)
    
    def show_warning(self, title: str, message: str, duration: int = 5000) -> bool:
        """显示警告通知"""
        return self.show_notification(f"⚠️ {title}", message, duration)
    
    def show_error(self, title: str, message: str, duration: int = 8000) -> bool:
        """显示错误通知"""
        return self.show_notification(f"❌ {title}", message, duration)
    
    def show_success(self, title: str, message: str, duration: int = 3000) -> bool:
        """显示成功通知"""
        return self.show_notification(f"✅ {title}", message, duration)


def create_system_notification() -> WindowsNotification:
    """创建系统通知实例"""
    return WindowsNotification()


# 全局通知实例
_system_notification = None

def get_notification() -> WindowsNotification:
    """获取全局通知实例"""
    global _system_notification
    if _system_notification is None:
        _system_notification = WindowsNotification()
    return _system_notification