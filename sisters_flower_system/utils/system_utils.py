"""
系统工具函数
提供系统相关的工具函数
"""

import os
import re
import sys
from datetime import date
from typing import Optional


def get_version_from_filename() -> str:
    """从当前文件/EXE名称中提取版本号"""
    try:
        # 获取当前程序路径（区分脚本和EXE）
        if getattr(sys, 'frozen', False):
            # EXE打包环境
            full_path = sys.executable
        else:
            # 脚本开发环境
            full_path = os.path.abspath(__file__)

        # 提取文件名（不含路径和扩展名）
        file_name = os.path.splitext(os.path.basename(full_path))[0]

        # 正则匹配：支持 (beta|v) 后带可选空格 + 数字（可带多个小数点）
        # 兼容：beta8、beta 8、beta1.1.1、beta 8.1.1、v1、v 2.3 等
        match = re.search(r'(beta|v)\s*\d+(\.\d+)*', file_name)  # 核心修改：增加 \s* 支持可选空格
        if match:
            return match.group().replace(" ", " ")  # 移除可能的空格，统一格式（如 beta 8 → beta8）
        return "unknown"  # 匹配失败时返回默认值
    except Exception as e:
        print(f"提取版本号失败: {e}")
        return "unknown"


class SingleInstance:
    """单实例控制类"""
    
    def __init__(self):
        self.mutex_name = "SistersFlowerSystem_{8F6F0AC4-B9A1-45FD-A8CF-72F04E6BDE8F}"  # 唯一标识
        try:
            import win32event
            import win32api
            self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
            self.last_error = win32api.GetLastError()
        except ImportError:
            # 在非Windows环境下，使用文件锁作为备选方案
            self._file_lock()
            self.last_error = 0
    
    def is_running(self) -> bool:
        """检查是否已有实例在运行"""
        # 直接使用错误代码183（对应ERROR_ALREADY_EXISTS），避免依赖win32con的定义
        return self.last_error == 183
    
    def _file_lock(self):
        """文件锁实现（Linux/Mac备选方案）"""
        import tempfile
        import fcntl
        
        # 创建锁文件
        lock_file_path = os.path.join(tempfile.gettempdir(), "sisters_flower_system.lock")
        try:
            self.lock_file = open(lock_file_path, 'w')
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
        except (IOError, OSError):
            # 锁文件已存在或无法创建，说明有实例在运行
            self.last_error = 183
            if hasattr(self, 'lock_file'):
                self.lock_file.close()
    
    def __del__(self):
        """析构函数，清理资源"""
        try:
            import win32api
            if hasattr(self, 'mutex') and self.mutex:
                win32api.CloseHandle(self.mutex)
        except (ImportError, AttributeError):
            # 非Windows环境或mutex不存在
            if hasattr(self, 'lock_file'):
                try:
                    self.lock_file.close()
                except:
                    pass


def check_festival() -> Optional[dict]:
    """检查当前是否为特定节日，返回节日信息"""
    today = date.today()
    
    # 情人节(2月14日)
    if today.month == 2 and today.day == 14:
        return {
            "name": "情人节",
            "greeting": "情人节快乐！今天销量肯定翻倍，备好货哦～",
            "title_suffix": "情人节特辑"
        }
    elif today.month == 3 and today.day == 8:
        return {
            "name": "妇女节",
            "greeting": "妇女节快乐！祝福所有妇女节日快乐哦～",
            "title_suffix": "妇女节特辑"
        }
    # 儿童节(6月1日)
    elif today.month == 6 and today.day == 1:
        return {
            "name": "儿童节",
            "greeting": "儿童节快乐！祝福所有儿童节日快乐哦～",
            "title_suffix": "儿童节特辑"
        }
    # 劳动节(5月1日)
    elif today.month == 5 and today.day == 1:
        return {
            "name": "劳动节",
            "greeting": "劳动节快乐！祝福所有劳动者们节日快乐哦～",
            "title_suffix": "劳动节特辑"
        }
    # 建党节(7月1日)
    elif today.month == 7 and today.day == 1:
        return {
            "name": "建党节",
            "greeting": "建党节快乐！祝福所有党员们节日快乐哦～",
            "title_suffix": "建党节特辑"
        }
    # 建军节(8月1日)
    elif today.month == 8 and today.day == 1:
        return {
            "name": "建军节",
            "greeting": "建军节快乐！祝福所有军人节日快乐哦～",
            "title_suffix": "建军节特辑"
        }
    # 教师节(9月1日)
    elif today.month == 9 and today.day == 10:
        return {
            "name": "教师节",
            "greeting": "教师节快乐！祝福所有教师节日快乐哦～",
            "title_suffix": "教师节特辑"
        }
    # 国庆节(10月1日)
    elif today.month == 10 and today.day == 1:
        return {
            "name": "国庆节",
            "greeting": "国庆节快乐！国庆佳节，祝祖国生日快乐！",
            "title_suffix": "国庆节特辑"
        }

    # 母亲节(5月14日)
    elif today.month == 5 and today.day == 14:
        return {
            "name": "母亲节",
            "greeting": "母亲节快乐！祝福所有母亲节日快乐哦～",
            "title_suffix": "母亲节特辑"
        }
    # 圣诞节(12月25日) - 改为元旦(1月1日)
    elif today.month == 1 and today.day == 1:
        return {
            "name": "元旦",
            "greeting": "元旦快乐！祝福所有亲戚朋友节日快乐哦～",
            "title_suffix": "元旦特辑"
        }
    # 花的生日(4月27日)
    elif today.month == 4 and today.day == 27:
        return {
            "name": "生日快乐",
            "greeting": "生日快乐！祝福花生日快乐！",
            "title_suffix": "生日特辑"
        }
    # 姐的生日(3月20日)
    elif today.month == 3 and today.day == 20:
        return {
            "name": "生日快乐",
            "greeting": "生日快乐！祝福姐生日快乐日快乐哦～",
            "title_suffix": "生日特辑"
        }
    # 妹的生日(3月28日)
    elif today.month == 3 and today.day == 28:
        return {
            "name": "生日快乐",
            "greeting": "生日快乐！祝福妹生日快乐哦～",
            "title_suffix": "生日特辑"
        }

    # 农历节日检查
    try:
        from lunar_python import Lunar, Solar
        
        # 1. 先创建公历对象（Solar）
        solar = Solar.fromYmd(today.year, today.month, today.day)
        # 2. 转换为农历对象（Lunar）
        lunar = solar.getLunar()
        lunar_month = lunar.getMonth()  # 农历月份
        lunar_day = lunar.getDay()  # 农历日期
    except Exception as e:
        print(f"农历转换错误: {e}")
        return None

    # 春节（正月初一）
    if lunar_month == 1 and lunar_day == 1:
        return {
            "name": "春节",
            "greeting": "春节快乐！阖家幸福，万事如意！",
            "title_suffix": "春节特辑"
        }
    # 元宵节（正月十五）
    elif lunar_month == 1 and lunar_day == 15:
        return {
            "name": "元宵节",
            "greeting": "元宵节快乐！记得吃汤圆哦～",
            "title_suffix": "元宵节特辑"
        }
    # 端午节（五月初五）
    elif lunar_month == 5 and lunar_day == 5:
        return {
            "name": "端午节",
            "greeting": "端午节快乐！祝您安康～",
            "title_suffix": "端午节特辑"
        }
    # 七夕节（七月初七）
    elif lunar_month == 7 and lunar_day == 7:
        return {
            "name": "七夕节",
            "greeting": "七夕节快乐！愿天下有情人终成眷属～",
            "title_suffix": "七夕特辑"
        }
    # 中秋节（八月十五）
    elif lunar_month == 8 and lunar_day == 15:
        return {
            "name": "中秋节",
            "greeting": "中秋节快乐！阖家团圆，幸福美满～",
            "title_suffix": "中秋节特辑"
        }
    # 重阳节（九月初九）
    elif lunar_month == 9 and lunar_day == 9:
        return {
            "name": "重阳节",
            "greeting": "重阳节快乐！祝长辈健康长寿～",
            "title_suffix": "重阳节特辑"
        }
    
    return None
