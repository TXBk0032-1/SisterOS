import base64
import configparser
import ctypes
import json
import os
import re
import sys
import threading
from ctypes import wintypes
from datetime import date
from tkinter import ttk, font, messagebox

import sqlite3

import win32api
import win32con
import win32event
import win32gui
from PIL import ImageTk, Image
from PIL._tkinter_finder import tk
from cryptography.hazmat.bindings._rust.openssl.aead import AESGCM
from lunar_python import Solar

from config import DB_PATH, THEME_CONFIG, SCALE_FACTOR

user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.SetTimer.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.LPVOID]
user32.SetTimer.restype = wintypes.UINT
user32.KillTimer.argtypes = [wintypes.HWND, wintypes.UINT]
user32.KillTimer.restype = wintypes.BOOL

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

def resource_path(relative_path):
    """获取资源文件的绝对路径（适配开发环境和打包后环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后的EXE环境：使用EXE所在目录作为基准路径
        base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境：使用当前脚本所在目录作为基准路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

"""加载配置文件"""
def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    config_path = resource_path("config.ini")  # 使用修正后的路径
    # 若配置文件不存在则在程序运行目录创建默认配置
    if not os.path.exists(config_path):
        config["push"] = {
            "interval": "5",
            "endpoint": "https://58e4706c.tw.cpolar.io/pushdata"
        }
        config["database"] = {
            "last_push_table": "push_status"
        }
        config["backup"] = {
            "enabled": "false",
            "time": "03:00",
            "interval_minutes": "30",
            "path": os.path.join(resource_path(""), "backups")  # 绝对路径
        }
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)
    config.read(config_path, encoding="utf-8")
    return config

# 新增保存配置的函数
def save_config_to_file():
    """保存配置到文件"""
    try:
        config_path = resource_path("config.ini")
        with open(config_path, "w", encoding="utf-8") as f:
            CONFIG.write(f)
        print("配置已成功保存到文件")
    except Exception as e:
        print(f"保存配置文件失败: {str(e)}")

# 加载配置（全局使用）
CONFIG = load_config()

def load_theme():
    """加载并返回上次保存的主题"""
    try:
        with open(resource_path(THEME_CONFIG), 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

def save_theme(theme_name):
    """保存当前主题"""
    try:
        with open(resource_path(THEME_CONFIG), 'w', encoding='utf-8') as f:
            f.write(theme_name)
    except Exception as e:
        print("Theme save error:", e)

# 添加配置存储函数（放在工具函数区域）
def save_exit_preference(choice, remember):
    """保存退出偏好设置"""
    config_path = resource_path("exit_preference.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section("Exit"):
        config.add_section("Exit")
    config.set("Exit", "choice", choice)  # "exit" 或 "tray"
    config.set("Exit", "remember", str(remember))
    with open(config_path, "w", encoding="utf-8") as f:
        config.write(f)

def load_exit_preference():
    """加载退出偏好设置"""
    config_path = resource_path("exit_preference.ini")
    if not os.path.exists(config_path):
        return None, False
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section("Exit"):
        return None, False
    choice = config.get("Exit", "choice", fallback=None)
    remember = config.getboolean("Exit", "remember", fallback=False)
    return choice, remember

def reset_exit_preference():
    """重置退出偏好设置"""
    config_path = resource_path("exit_preference.ini")
    if os.path.exists(config_path):
        os.remove(config_path)

def init_db():
    """初始化或升级数据库结构"""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    cur = conn.cursor()

    # users 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            avatar TEXT
        )
    """)

    # 检查是否已有 avatar 字段（兼容老库）
    cur.execute("PRAGMA table_info(users)")
    cols = {r[1] for r in cur.fetchall()}
    if 'avatar' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN avatar TEXT")
        cur.execute("UPDATE users SET avatar = 'profile_photo.png' WHERE avatar IS NULL")

    # 检查用户表是否为空，若空则插入默认用户
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        default_avatar = "profile_photo.png"
        cur.execute(
            "INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)",
            ("a", "123", default_avatar)
        )

    # members 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            balance REAL DEFAULT 0,
            remark TEXT,
            join_date TEXT
        )
    """)
    # 检查是否已有join_date字段（兼容老库）
    cur.execute("PRAGMA table_info(members)")
    cols = {r[1] for r in cur.fetchall()}
    if 'join_date' not in cols:
        cur.execute("ALTER TABLE members ADD COLUMN join_date TEXT")
        # 为现有会员设置默认日期
        cur.execute("UPDATE members SET join_date = datetime('now', 'localtime') WHERE join_date IS NULL")

    # inventory 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT UNIQUE,
            price REAL DEFAULT 0,
            member_price REAL DEFAULT 0,
            remark TEXT
        )
    """)

    # 移除库存 stock 字段（兼容升级）
    cur.execute("PRAGMA table_info(inventory)")
    cols = {r[1] for r in cur.fetchall()}
    if 'stock' in cols:
        # SQLite 不支持直接 DROP COLUMN，这里需要迁移表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory_new (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT UNIQUE,
                price REAL DEFAULT 0,
                member_price REAL DEFAULT 0,
                remark TEXT
            )
        """)
        cur.execute("""
            INSERT INTO inventory_new (item_id, category, name, price, member_price, remark)
            SELECT item_id, category, name, price, member_price, remark FROM inventory
        """)
        cur.execute("DROP TABLE inventory")
        cur.execute("ALTER TABLE inventory_new RENAME TO inventory")

    # sales 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            total_due REAL NOT NULL,
            total_paid REAL NOT NULL,
            is_member INTEGER NOT NULL DEFAULT 0
        )
    """)
    cur.execute("PRAGMA table_info(sales)")
    cols = {r[1] for r in cur.fetchall()}
    if 'member_phone' not in cols:
        cur.execute("ALTER TABLE sales ADD COLUMN member_phone TEXT")

    # sale_items 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            category TEXT,
            name TEXT,
            price REAL,
            quantity INTEGER,
            remark TEXT,
            FOREIGN KEY(sale_id) REFERENCES sales(sale_id)
        )
    """)
    cur.execute("PRAGMA table_info(sale_items)")
    cols = {r[1] for r in cur.fetchall()}
    if 'remark' not in cols:
        cur.execute("ALTER TABLE sale_items ADD COLUMN remark TEXT")

    # memory_reminder 表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memory_reminder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_reminder_date TEXT NOT NULL,
            reminder_interval INTEGER NOT NULL
        )
    """)

    # last_push_table
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {CONFIG['database']['last_push_table']} (
            table_name TEXT PRIMARY KEY,
            last_push_time TEXT NOT NULL DEFAULT '2000-01-01 00:00:00'
        )
    """)
    for table in ["sales", "inventory", "accounting"]:
        cur.execute(f"""
            INSERT OR IGNORE INTO {CONFIG['database']['last_push_table']} 
            (table_name, last_push_time) VALUES (?, ?)
        """, (table, '2000-01-01 00:00:00'))

        # 销售目标表
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sales_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_type TEXT NOT NULL,
                target_date TEXT NOT NULL,
                target_amount REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 确保每天/每月都有一个默认目标（如果不存在）
        today = date.today()
        day_key = today.strftime("%Y-%m-%d")
        month_key = today.strftime("%Y-%m")

        # 检查今日目标是否存在
        cur.execute("SELECT id FROM sales_goals WHERE period_type=? AND target_date=?",
                    ("day", day_key))
        if not cur.fetchone():
            # 若今日目标不存在，查询最近一次设置的每日目标（任意日期）
            cur.execute("""
                    SELECT target_amount FROM sales_goals 
                    WHERE period_type='day' 
                    ORDER BY target_date DESC 
                    LIMIT 1
                """)
            last_day_goal = cur.fetchone()

            if last_day_goal:
                # 存在历史每日目标，自动继承为今日目标
                cur.execute("""
                        INSERT INTO sales_goals (period_type, target_date, target_amount)
                        VALUES (?, ?, ?)
                    """, ("day", day_key, last_day_goal[0]))
            else:
                # 首次使用（无任何历史目标），可设置一个初始默认值或留空
                # 若希望完全手动设置，可删除以下代码（首次使用时目标为0，需手动设置）
                cur.execute("""
                        INSERT INTO sales_goals (period_type, target_date, target_amount)
                        VALUES (?, ?, 5000)
                    """, ("day", day_key))

        # 检查当月目标是否存在，不存在则创建默认值
        cur.execute("SELECT id FROM sales_goals WHERE period_type=? AND target_date=?",
                    ("month", month_key))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO sales_goals (period_type, target_date, target_amount)
                VALUES (?, ?, 150000)
            """, ("month", month_key))

    # 记录统计彩蛋
    cur.execute("SELECT COUNT(*) FROM sales")
    sale_count = cur.fetchone()[0]
    if sale_count >= 1000 and sale_count % 1000 == 0:
        conn.commit()
        conn.close()
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("里程碑", f"恭喜！系统已记录第{sale_count}笔销售，再创佳绩！")
        return

    conn.commit()
    return conn

def configure_scaling_and_font(root):
    """统一设置缩放和全局字体"""
    root.tk.call('tk', 'scaling', SCALE_FACTOR)
    base_font = font.nametofont("TkDefaultFont")
    base_font.configure(family="Microsoft YaHei", size=int(10 * SCALE_FACTOR))
    style = ttk.Style()
    style.configure('.', font=(base_font.actual('family'), base_font.actual('size')))
    style.configure('Treeview', rowheight=int(24 * SCALE_FACTOR))

def make_table(parent, cols):
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


def get_version_from_filename():
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

# 在工具函数区域添加节日检查函数
def check_festival():
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
    # 圣诞节(12月25日)
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

    try:
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

# Key 文件路径（放在程序同目录）
KEY_PATH = os.path.join(os.path.dirname(__file__), 'nfc_key.bin')

def generate_key(force=False):
    if os.path.exists(KEY_PATH) and not force:
        return load_key()
    key = AESGCM.generate_key(bit_length=256)
    with open(KEY_PATH, 'wb') as f:
        f.write(key)
    try:
        os.chmod(KEY_PATH, 0o600)
    except Exception:
        pass
    return key

def load_key():
    if not os.path.exists(KEY_PATH):
        return generate_key()
    with open(KEY_PATH, 'rb') as f:
        return f.read()

def encrypt_credentials(username: str, password: str, key=None):
    """返回 dict（json 可序列化），data 为 base64(nonce + ciphertext + tag)"""
    if key is None:
        key = load_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    payload = json.dumps({"u": username, "p": password}, ensure_ascii=False).encode('utf-8')
    ct = aesgcm.encrypt(nonce, payload, None)  # ct includes tag at end
    blob = nonce + ct
    return {"v":1, "type":"login", "data": base64.b64encode(blob).decode('ascii')}

def decrypt_credentials(record: dict, key=None):
    if key is None:
        key = load_key()
    if record.get("v") != 1 or record.get("type") != "login":
        raise ValueError("Unsupported record")
    blob = base64.b64decode(record["data"].encode('ascii'))
    nonce, ct = blob[:12], blob[12:]
    aesgcm = AESGCM(key)
    payload = aesgcm.decrypt(nonce, ct, None)
    d = json.loads(payload.decode('utf-8'))
    return d["u"], d["p"]

# --- pyscard MIFARE Classic style read/write using ACR122 APDUs ---
# APDU patterns for ACR122 / PCSC readers (works in many setups)
def _send_apdu(conn, apdu):
    """发送 APDU，返回 (response_bytes, sw1, sw2)"""
    resp, sw1, sw2 = conn.transmit(apdu)
    return bytes(resp), sw1, sw2

def load_mifare_key(conn, key=b'\xff'*6, key_number=0x00):
    """Load key into reader key slot (key_number 0x00..0x01 etc)"""
    if len(key) != 6:
        raise ValueError("MIFARE key must be 6 bytes")
    apdu = [0xFF, 0x82, 0x00, key_number, 0x06] + list(key)
    _, sw1, sw2 = conn.transmit(apdu)
    return (sw1, sw2) == (0x90, 0x00)

def authenticate_block(conn, block_number, key_number=0x00, key_type=0x60):
    """
    key_type: 0x60 = Key A, 0x61 = Key B
    Use APDU: FF 86 00 00 05 01 00 <block> <key_type> <key_number>
    """
    apdu = [0xFF, 0x86, 0x00, 0x00, 0x05,
            0x01, 0x00, block_number, key_type, key_number]
    _, sw1, sw2 = conn.transmit(apdu)
    return (sw1, sw2) == (0x90, 0x00)

def read_block(conn, block_number):
    """Read 16 bytes from block. Returns bytes or raise."""
    apdu = [0xFF, 0xB0, 0x00, block_number, 0x10]
    resp, sw1, sw2 = conn.transmit(apdu)
    if (sw1, sw2) != (0x90, 0x00):
        raise RuntimeError(f"Read block {block_number} failed: SW={hex(sw1)} {hex(sw2)}")
    return bytes(resp)

# 添加销售目标相关工具函数
def get_sales_goal(period_type, target_date):
    """获取指定周期的销售目标"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT target_amount FROM sales_goals 
        WHERE period_type=? AND target_date=?
    """, (period_type, target_date))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0


def update_sales_goal(period_type, target_date, amount):
    """更新指定周期的销售目标"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # 先尝试更新
    cur.execute("""
        UPDATE sales_goals SET target_amount=? 
        WHERE period_type=? AND target_date=?
    """, (amount, period_type, target_date))

    # 如果没有更新任何记录，则插入新记录
    if cur.rowcount == 0:
        cur.execute("""
            INSERT INTO sales_goals (period_type, target_date, target_amount)
            VALUES (?, ?, ?)
        """, (period_type, target_date, amount))

    conn.commit()
    conn.close()


def get_current_period_sales(period_type):
    """获取当前周期的销售总额"""
    today = date.today()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if period_type == "day":
        # 今日销售额
        date_str = today.strftime("%Y-%m-%d")
        cur.execute("""
            SELECT SUM(total_paid) FROM sales 
            WHERE datetime LIKE ?
        """, (f"{date_str}%",))
    else:
        # 当月销售额
        month_str = today.strftime("%Y-%m")
        cur.execute("""
            SELECT SUM(total_paid) FROM sales 
            WHERE datetime LIKE ?
        """, (f"{month_str}%",))

    result = cur.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0


def get_sales_progress(period_type):
    """获取当前周期的销售进度（完成比例）"""
    today = date.today()
    target_date = today.strftime("%Y-%m-%d") if period_type == "day" else today.strftime("%Y-%m")

    goal = get_sales_goal(period_type, target_date)
    if goal <= 0:
        return 0, 0, 0  # 目标为0时，进度为0

    sales = get_current_period_sales(period_type)
    progress = min(100, (sales / goal) * 100)  # 最大100%
    return progress, sales, goal

# 全局版本号变量（程序启动时自动提取）
APP_VERSION = get_version_from_filename()

# 在全局配置区域添加单实例控制代码
class SingleInstance:
    def __init__(self):
        self.mutex_name = "SistersFlowerSystem_{8F6F0AC4-B9A1-45FD-A8CF-72F04E6BDE8F}"  # 唯一标识
        self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
        self.last_error = win32api.GetLastError()

    def is_running(self):
        # 直接使用错误代码183（对应ERROR_ALREADY_EXISTS），避免依赖win32con的定义
        return self.last_error == 183

    def __del__(self):
        if hasattr(self, 'mutex') and self.mutex:
            win32api.CloseHandle(self.mutex)

class AvatarCropper:
    def __init__(self, parent, image_path):
        self.top = tk.Toplevel(parent)
        self.top.title("裁剪头像")
        self.image_path = image_path
        self.cropped_image = None  # 存储裁剪结果

        # 安全加载图片
        self.original_img = Image.open(image_path)  # 假设已实现safe_open_image
        self.base_img = self.original_img.copy()  # 保留原始尺寸用于计算
        self.scale_factor = 1.0  # 图片缩放系数
        self.offset_x = 0  # 图片偏移量（相对于画布）
        self.offset_y = 0  # 图片偏移量（相对于画布）

        # 画布尺寸
        self.canvas_width = 800
        self.canvas_height = 600
        self.canvas = tk.Canvas(
            self.top,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#f0f0f0"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 固定取景框（居中显示，大小200x200，可根据需求调整）
        self.crop_size = 200
        self.crop_x1 = (self.canvas_width - self.crop_size) // 2
        self.crop_y1 = (self.canvas_height - self.crop_size) // 2
        self.crop_x2 = self.crop_x1 + self.crop_size
        self.crop_y2 = self.crop_y1 + self.crop_size

        # 创建固定取景框
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_x1, self.crop_y1, self.crop_x2, self.crop_y2,
            outline="red", width=2, dash=(5, 2)
        )

        # 初始显示图片（居中）
        self.initial_image_position()
        self.update_display_image()

        # 绘制遮罩（固定在取景框周围）
        self.mask_items = []
        self.draw_mask()

        # 绑定事件（改为拖动图片，而非取景框）
        self.canvas.bind("<Button-1>", self.start_drag_image)
        self.canvas.bind("<B1-Motion>", self.drag_image)
        self.canvas.bind("<MouseWheel>", self.zoom_image)  # 滚轮缩放图片
        self.canvas.bind("<Button-3>", self.reset_view)  # 右键重置视图

        # 按钮
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="确认裁剪", command=self.crop).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.top.destroy).pack(side=tk.LEFT, padx=5)

        # 状态变量
        self.dragging_image = False
        self.start_drag_x = 0
        self.start_drag_y = 0

    def initial_image_position(self):
        """初始化图片位置（居中显示）"""
        # 计算初始缩放系数（确保图片能完整显示在画布中）
        img_width, img_height = self.base_img.size
        scale_w = self.canvas_width / img_width
        scale_h = self.canvas_height / img_height
        self.scale_factor = min(scale_w, scale_h) * 0.9  # 留10%边距

        # 初始偏移量（居中）
        self.offset_x = self.canvas_width // 2
        self.offset_y = self.canvas_height // 2

    def update_display_image(self):
        """更新显示的图片（考虑缩放和偏移）"""
        # 计算缩放后的图片尺寸
        img_width, img_height = self.base_img.size
        scaled_width = int(img_width * self.scale_factor)
        scaled_height = int(img_height * self.scale_factor)

        # 缩放图片
        self.scaled_img = self.base_img.resize(
            (scaled_width, scaled_height),
            Image.Resampling.LANCZOS
        )

        # 转换为Tkinter可用格式
        self.tk_image = ImageTk.PhotoImage(self.scaled_img)

        # 更新画布图片
        if hasattr(self, 'image_id'):
            self.canvas.delete(self.image_id)
        # 图片锚点为中心，基于偏移量定位
        self.image_id = self.canvas.create_image(
            self.offset_x, self.offset_y,
            image=self.tk_image,
            anchor=tk.CENTER
        )
        self.canvas.tag_lower(self.image_id)  # 确保图片在底层
        self.canvas.tag_raise(self.crop_rect)  # 确保取景框在顶层

    def draw_mask(self):
        """绘制取景框外的遮罩（固定位置）"""
        # 清除旧遮罩
        for item in self.mask_items:
            self.canvas.delete(item)
        self.mask_items = []

        # 遮罩颜色（半透明灰色）
        mask_color = "#888888"
        # 绘制取景框周围的四个遮罩区域
        self.mask_items.extend([
            # 左方遮罩
            self.canvas.create_rectangle(
                0, 0, self.crop_x1, self.canvas_height,
                fill=mask_color, outline="", stipple="gray50"
            ),
            # 右方遮罩
            self.canvas.create_rectangle(
                self.crop_x2, 0, self.canvas_width, self.canvas_height,
                fill=mask_color, outline="", stipple="gray50"
            ),
            # 上方遮罩
            self.canvas.create_rectangle(
                self.crop_x1, 0, self.crop_x2, self.crop_y1,
                fill=mask_color, outline="", stipple="gray50"
            ),
            # 下方遮罩
            self.canvas.create_rectangle(
                self.crop_x1, self.crop_y2, self.crop_x2, self.canvas_height,
                fill=mask_color, outline="", stipple="gray50"
            )
        ])
        self.canvas.tag_raise(self.crop_rect)  # 确保取景框在顶层

    def start_drag_image(self, event):
        """开始拖拽图片"""
        # 检查点击位置是否在图片上
        img_width, img_height = self.scaled_img.size
        img_x1 = self.offset_x - img_width // 2
        img_y1 = self.offset_y - img_height // 2
        img_x2 = self.offset_x + img_width // 2
        img_y2 = self.offset_y + img_height // 2

        if img_x1 <= event.x <= img_x2 and img_y1 <= event.y <= img_y2:
            self.dragging_image = True
            self.start_drag_x = event.x
            self.start_drag_y = event.y

    def drag_image(self, event):
        """拖拽图片（移动图片位置）"""
        if not self.dragging_image:
            return

        # 计算移动距离
        dx = event.x - self.start_drag_x
        dy = event.y - self.start_drag_y

        # 更新图片偏移量
        self.offset_x += dx
        self.offset_y += dy

        # 更新显示
        self.update_display_image()
        self.start_drag_x = event.x
        self.start_drag_y = event.y

    def zoom_image(self, event):
        """缩放图片（滚轮控制）"""
        # 记录当前鼠标在画布上的位置
        mouse_x, mouse_y = event.x, event.y

        # 计算新缩放系数
        old_scale = self.scale_factor
        if event.delta > 0:
            self.scale_factor = min(5.0, self.scale_factor * 1.1)  # 最大放大5倍
        else:
            self.scale_factor = max(0.2, self.scale_factor / 1.1)  # 最小缩小到0.2倍

        # 以鼠标位置为中心缩放（保持鼠标指向的图片位置不变）
        # 计算公式：新偏移量 = 鼠标位置 - (鼠标位置 - 旧偏移量) * (新缩放 / 旧缩放)
        self.offset_x = mouse_x - (mouse_x - self.offset_x) * (self.scale_factor / old_scale)
        self.offset_y = mouse_y - (mouse_y - self.offset_y) * (self.scale_factor / old_scale)

        # 更新显示
        self.update_display_image()

    def reset_view(self, event):
        """重置视图（右键点击）"""
        self.initial_image_position()
        self.update_display_image()
        self.draw_mask()

    def crop(self):
        """执行裁剪（计算固定取景框对应的图片区域）"""
        # 1. 获取图片在画布上的显示区域（缩放后的位置和尺寸）
        scaled_width = int(self.base_img.width * self.scale_factor)
        scaled_height = int(self.base_img.height * self.scale_factor)
        img_display_x1 = self.offset_x - scaled_width // 2
        img_display_y1 = self.offset_y - scaled_height // 2

        # 2. 计算固定取景框与图片显示区域的重叠部分
        overlap_x1 = max(self.crop_x1, img_display_x1)
        overlap_y1 = max(self.crop_y1, img_display_y1)
        overlap_x2 = min(self.crop_x2, img_display_x1 + scaled_width)
        overlap_y2 = min(self.crop_y2, img_display_y1 + scaled_height)

        # 3. 检查是否有重叠区域
        if overlap_x1 >= overlap_x2 or overlap_y1 >= overlap_y2:
            messagebox.showerror("错误", "请确保取景框内有图片内容")
            return

        # 4. 将重叠区域转换为缩放后图片上的坐标（相对图片左上角）
        img_rel_x1 = overlap_x1 - img_display_x1
        img_rel_y1 = overlap_y1 - img_display_y1
        img_rel_x2 = overlap_x2 - img_display_x1
        img_rel_y2 = overlap_y2 - img_display_y1

        # 5. 将缩放后图片的坐标转换为原始图片的坐标
        orig_x1 = int(img_rel_x1 / self.scale_factor)
        orig_y1 = int(img_rel_y1 / self.scale_factor)
        orig_x2 = int(img_rel_x2 / self.scale_factor)
        orig_y2 = int(img_rel_y2 / self.scale_factor)

        # 6. 执行裁剪
        self.cropped_image = self.original_img.crop((orig_x1, orig_y1, orig_x2, orig_y2))

        # 释放资源并关闭窗口
        self.original_img.close()
        self.top.destroy()

class WindowsNotification:
    def __init__(self, title, message, icon_path=None, duration=10):
        self.title = title
        self.message = message
        self.icon_path = icon_path
        self.duration = duration * 1000  # 转换为毫秒
        self.hwnd = None
        self.notify_id = 1001  # 通知唯一标识
        self.timer_id = None  # 定时器ID
        self.class_atom = None  # 新增：保存窗口类原子值
        # 生成唯一类名（使用线程ID确保唯一性）
        self.class_name = f"NotificationClass_{threading.get_ident()}"

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """窗口消息处理函数"""
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        elif msg == win32con.WM_TIMER:
            # 处理定时器事件
            self._on_timer()
            return 0
        elif msg == win32con.WM_COMMAND:
            return 0
        # 其他消息使用默认处理
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _create_window(self):
        """创建隐藏窗口用于处理通知消息"""
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = self.class_name  # 使用唯一类名
        self.class_atom = win32gui.RegisterClass(wc)  # 保存类原子
        self.hwnd = win32gui.CreateWindow(
            self.class_atom, "Notification Window", 0, 0, 0,
            win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
            0, 0, wc.hInstance, None
        )
        win32gui.UpdateWindow(self.hwnd)

    def _load_icon(self):
        """加载通知图标"""
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                return win32gui.LoadImage(
                    win32api.GetModuleHandle(None),
                    self.icon_path,
                    win32con.IMAGE_ICON,
                    0, 0,
                    win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                )
            except:
                pass
        # 加载默认图标
        return win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

    # 修改WindowsNotification类中的show()方法里的消息循环部分
    def show(self):
        """显示系统通知"""
        try:  # 增加try-finally确保资源释放
            self._create_window()
            hicon = self._load_icon()

            # 初始化通知图标
            nid = (
                self.hwnd, self.notify_id,
                win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                win32con.WM_USER + 20, hicon, "姐妹花销售系统"
            )
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

            # 更新通知内容
            nid = (
                self.hwnd, self.notify_id,
                win32gui.NIF_INFO,
                win32con.WM_USER + 20, hicon,
                "通知", self.message, 200, self.title
            )
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

            # 调用底层 SetTimer API
            self.timer_id = user32.SetTimer(
                self.hwnd,  # 窗口句柄
                0,  # 定时器ID（0表示自动分配）
                self.duration,  # 超时时间（毫秒）
                None  # 回调函数（通过WM_TIMER消息处理）
            )
            if not self.timer_id:
                raise ctypes.WinError(ctypes.get_last_error())

            # 消息循环
            while True:
                # GetMessage实际返回值为 (msg, wparam, lparam) 或 (False,) 当无消息时
                msg_result = win32gui.GetMessage(None, 0, 0)

                # 检查是否有消息（返回值长度为3表示有消息）
                if len(msg_result) != 3:
                    break  # 无消息时退出循环

                msg, wparam, lparam = msg_result

                # 传递消息给翻译和分发函数
                win32gui.TranslateMessage((msg, wparam, lparam))
                win32gui.DispatchMessage((msg, wparam, lparam))

                # 检查退出消息
                if msg == win32con.WM_QUIT:
                    break
        finally:
            # 清理资源
            if self.timer_id:
                user32.KillTimer(self.hwnd, self.timer_id)
            # 删除通知图标
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, self.notify_id))
            # 销毁窗口
            if self.hwnd:
                win32gui.DestroyWindow(self.hwnd)
            # 注销窗口类（关键修复）
            if self.class_atom:
                try:
                    win32gui.UnregisterClass(self.class_atom, win32api.GetModuleHandle(None))
                except:
                    pass
