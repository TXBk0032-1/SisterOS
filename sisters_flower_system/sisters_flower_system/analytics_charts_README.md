# 数据分析图表模块

完整的数据分析和图表展示模块，为花店系统提供专业的数据可视化功能。

## 功能特点

### 📊 图表类型
- **销售趋势图表**: 折线图和柱状图展示销售走势
- **商品销售占比**: 饼图和环形图展示商品销售分布
- **客户分析图表**: 客户类型分布和数量统计
- **库存分析图表**: 库存状态监控和预警
- **财务报表图表**: 收入、支出、利润趋势分析

### 🔄 交互功能
- 实时数据更新（可配置自动刷新间隔）
- 图表类型切换
- 时间范围选择（7天、30天、90天、1年）
- 鼠标悬停和点击交互
- 全屏显示模式

### 💾 导出功能
- **图片导出**: PNG、PDF格式
- **数据导出**: Excel格式（包含详细数据）
- **打印功能**: 直接打印图表

### 🎯 实用功能
- 库存预警系统
- 实时数据面板
- 多线程数据处理
- 错误处理和异常管理

## 快速开始

### 1. 运行演示
```bash
python analytics_demo.py
```

### 2. 集成到现有系统
```python
from gui.analytics_charts_gui import AnalyticsChartsGUI, DataAnalyticsPanel
import tkinter as tk

# 创建主窗口
root = tk.Tk()
root.title("花店管理系统")

# 添加数据分析面板
analytics_panel = DataAnalyticsPanel(root)
analytics_panel.pack(fill='both', expand=True)

root.mainloop()
```

### 3. 创建特定图表
```python
from gui.analytics_charts_gui import AnalyticsChartsGUI
import tkinter as tk

# 创建窗口
window = tk.Toplevel()
window.title("销售分析")
window.geometry("1200x800")

# 创建图表界面
analytics = AnalyticsChartsGUI(window)
analytics.current_chart_type.set("sales_trend")  # 设置图表类型
analytics.update_chart()  # 更新图表
analytics.pack(fill='both', expand=True)
```

## 图表类型说明

### 1. 销售趋势 (sales_trend)
- **折线图**: 显示每日销售趋势
- **柱状图**: 显示销售数据分布
- **统计信息**: 总销售额、平均销售额、最高/最低销售额

### 2. 商品销售占比 (product_sales)
- **饼图**: 商品销售比例
- **环形图**: 另一种销售占比展示
- **排行图**: 商品销售数量排行

### 3. 客户分析 (customer_analysis)
- **饼图**: 客户类型分布
- **柱状图**: 各类客户数量统计
- **分析报告**: 客户统计信息

### 4. 库存分析 (inventory_analysis)
- **对比图**: 当前库存与最低/最高库存对比
- **预警图**: 库存不足商品标识
- **统计报告**: 库存统计和预警信息

### 5. 财务报表 (financial_report)
- **趋势图**: 收入和支出趋势
- **利润图**: 利润变化趋势
- **财务统计**: 收入、支出、利润汇总

## 高级功能

### 自动刷新
```python
# 启用自动刷新
analytics.auto_refresh_var.set(True)

# 设置刷新间隔（秒）
analytics.refresh_interval_var.set("30")
```

### 自定义数据源
```python
class CustomChartManager(ChartManager):
    def get_sales_data(self, days: int = 30):
        # 从数据库获取真实数据
        # 实现您的数据获取逻辑
        return data

# 使用自定义管理器
analytics.chart_manager = CustomChartManager()
```

### 事件处理
```python
# 图表点击事件
def on_chart_click(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        print(f"点击坐标: x={x:.2f}, y={y:.2f}")

# 绑定事件
analytics.canvas.mpl_connect('button_press_event', on_chart_click)
```

## 导出功能详解

### 图片导出
```python
# 导出PNG格式
analytics.export_chart('png')

# 导出PDF格式
analytics.export_chart('pdf')
```

### Excel数据导出
```python
# 导出当前图表数据到Excel
analytics.export_excel()
```

### 打印功能
```python
# 直接打印图表
analytics.print_chart()
```

## 配置选项

### 时间范围
- 7天：短期销售趋势
- 30天：月度销售分析（默认）
- 90天：季度销售趋势
- 1年：年度销售分析

### 自动刷新设置
- 启用/禁用自动刷新
- 可配置刷新间隔（1-3600秒）
- 实时数据面板每5秒更新

## 依赖要求

### 必需依赖
- `tkinter` - GUI框架（Python内置）
- `matplotlib` - 图表绘制
- `pandas` - 数据处理
- `numpy` - 数值计算

### 安装命令
```bash
pip install matplotlib pandas numpy
```

## 故障排除

### 常见问题

1. **导入错误**
   - 确保所有依赖包已安装
   - 检查Python路径设置

2. **图表显示问题**
   - 确认matplotlib后端设置正确
   - 检查显示器分辨率和DPI设置

3. **性能问题**
   - 减少数据点数量
   - 调整自动刷新间隔
   - 使用数据缓存

4. **导出失败**
   - 检查文件路径权限
   - 确保有足够的磁盘空间

### 调试模式
```python
# 启用调试输出
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展开发

### 添加新图表类型
1. 在`ChartManager`中添加数据获取方法
2. 在`AnalyticsChartsGUI.update_chart()`中添加处理逻辑
3. 在控制面板中添加新的选项

### 自定义样式
```python
# 修改图表样式
plt.style.use('seaborn')  # 使用 seaborn 样式
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
```

## 版本信息

- **版本**: 1.0.0
- **作者**: Sisters Flower System
- **更新日期**: 2025-11-08
- **Python版本**: 3.7+

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。

---

*此模块是Sisters Flower System的一部分，提供了完整的数据分析和可视化解决方案。*