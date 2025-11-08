"""
Win11 主题配置
提供现代化的Win11风格颜色主题
"""

class Win11Theme:
    """Win11风格主题配置"""
    
    def __init__(self):
        # 基础颜色
        self.colors = {
            # 主要颜色
            'primary': '#0078D4',      # Microsoft Blue
            'secondary': '#106EBE',    # 较深的蓝色
            'accent': '#FFC83D',       # 金黄色
            
            # 语义化颜色
            'success': '#107C10',      # 绿色
            'warning': '#FF8C00',      # 橙色
            'error': '#D83B01',        # 红色
            'info': '#00BCF2',         # 青色
            
            # 背景色
            'background': '#FAFAFA',   # 浅灰白
            'surface': '#FFFFFF',      # 纯白
            'surface_variant': '#F3F2F1',  # 浅灰
            'outline': '#EDEBE9',      # 边框灰
            
            # 文本颜色
            'text_primary': '#323130',     # 深灰
            'text_secondary': '#605E5C',   # 中灰
            'text_disabled': '#A19F9D',   # 浅灰
            
            # 交互状态
            'hover': '#F3F2F1',
            'pressed': '#E1DFDD',
            'focus': '#0078D4',
            
            # 特殊效果
            'shadow': 'rgba(0, 0, 0, 0.1)',
            'overlay': 'rgba(0, 0, 0, 0.4)'
        }
        
        # 字体配置
        self.fonts = {
            'default': ('Segoe UI', 9),
            'caption': ('Segoe UI', 8),
            'body': ('Segoe UI', 9),
            'subheading': ('Segoe UI', 10, 'bold'),
            'heading': ('Segoe UI', 12, 'bold'),
            'title': ('Segoe UI', 16, 'bold'),
            'display': ('Segoe UI', 20, 'bold')
        }
        
        # 尺寸配置
        self.spacing = {
            'xs': 4,
            'sm': 8,
            'md': 16,
            'lg': 24,
            'xl': 32,
            'xxl': 48
        }
        
        # 圆角配置
        self.radius = {
            'small': 4,
            'medium': 8,
            'large': 12,
            'circle': 50
        }
        
        # 阴影配置
        self.shadows = {
            'small': '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
            'medium': '0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23)',
            'large': '0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23)'
        }
    
    def apply_theme(self, root):
        """应用主题到Tkinter根窗口"""
        # 设置默认字体
        root.option_add("*Font", self.fonts['default'])
        
        # 设置主题色彩（如果使用ttk）
        try:
            from tkinter import ttk
            style = ttk.Style()
            style.theme_use('clam')  # 使用clam主题作为基础
            
            # 配置ttk样式
            self._configure_ttk_styles(style)
        except ImportError:
            pass
    
    def _configure_ttk_styles(self, style):
        """配置ttk样式"""
        # 按钮样式
        style.configure('Win11.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=self.fonts['body'])
        
        style.map('Win11.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['pressed'])])
        
        # 标签框架样式
        style.configure('Win11.TLabelframe',
                       background=self.colors['surface'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['outline'])
        
        style.configure('Win11.TLabelframe.Label',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['subheading'])
        
        # 笔记本样式
        style.configure('Win11.TNotebook',
                       background=self.colors['surface'],
                       borderwidth=0)
        
        style.configure('Win11.TNotebook.Tab',
                       background=self.colors['surface_variant'],
                       foreground=self.colors['text_secondary'],
                       padding=[20, 10],
                       font=self.fonts['body'])
        
        style.map('Win11.TNotebook.Tab',
                 background=[('selected', self.colors['surface']),
                           ('active', self.colors['hover'])])
        
        # 表格样式
        style.configure('Win11.Treeview',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['surface'],
                       borderwidth=1,
                       relief='solid',
                       rowheight=25)
        
        style.configure('Win11.Treeview.Heading',
                       background=self.colors['surface_variant'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['subheading'],
                       borderwidth=0)
        
        style.map('Win11.Treeview',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        # 输入框样式
        style.configure('Win11.TEntry',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       padding=[8, 4])
        
        # 标签样式
        style.configure('Win11.TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       font=self.fonts['body'])


# 创建全局实例
win11_theme = Win11Theme()

# 便捷方法
def apply_theme(root):
    """应用Win11主题到指定窗口"""
    win11_theme.apply_theme(root)

def get_color(color_name):
    """获取指定颜色"""
    return win11_theme.colors.get(color_name, '#000000')

def get_font(font_name, size=None, weight='normal'):
    """获取指定字体"""
    font_config = win11_theme.fonts.get(font_name, ('Segoe UI', 9))
    if size is not None:
        font_config = (font_config[0], size)
    if weight != 'normal':
        font_config = font_config + (weight,)
    return font_config