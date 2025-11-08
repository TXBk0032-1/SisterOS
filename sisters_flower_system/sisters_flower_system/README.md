# 🌸 姐妹花销售系统 v4.0

![Version](https://img.shields.io/badge/version-4.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

姐妹花销售系统是一个现代化的销售管理解决方案，专为小型到中型企业设计。系统提供完整的销售流程管理、数据分析、库存控制和用户权限管理功能。

## ✨ 主要特性

### 🎯 核心功能
- **销售管理**: 完整的销售流程，从开单到收银
- **库存管理**: 实时库存跟踪，自动预警
- **客户管理**: 客户信息维护，购买历史追踪
- **财务报表**: 自动生成各种财务报表
- **数据分析**: 销售趋势分析，经营数据可视化

### 🎨 用户界面
- **现代化设计**: 基于Win11 Fluent Design语言
- **响应式布局**: 适配不同屏幕尺寸
- **主题切换**: 支持明暗主题
- **多语言支持**: 简体中文/English

### 🛡️ 系统安全
- **用户认证**: 基于角色的访问控制
- **会话管理**: 自动超时和安全退出
- **操作审计**: 完整的行为记录
- **数据加密**: 敏感信息加密存储

### 🔧 技术特性
- **跨平台**: Windows/Linux/macOS支持
- **数据库**: SQLite（可扩展到MySQL/PostgreSQL）
- **模块化**: 组件化设计，易于扩展
- **自动化**: 定时备份，系统监控

## 🚀 快速开始

### 一键安装
```bash
# Windows用户
install_windows.bat

# Linux/macOS用户
chmod +x install_linux.sh && ./install_linux.sh

# 通用快速启动
python quick_start.py
```

### 手动安装
1. **检查Python环境**
   ```bash
   python --version  # 需要 3.8+
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化系统**
   ```bash
   python install.py
   ```

4. **启动应用**
   ```bash
   python enhanced_sales_system.py
   ```

### 使用管理工具
```bash
# 图形化管理界面
python system_manager.py --gui

# 系统监控
python system_monitor.py monitor

# 备份管理
python backup_recovery.py list
```

## 📁 项目结构

```
sisters_flower_system/
├── 📄 enhanced_sales_system.py      # 主程序入口
├── 📄 install.py                    # 自动安装脚本
├── 📄 quick_start.py                # 快速启动工具
├── 📄 system_manager.py             # 统一管理工具
├── 📄 service_manager.py            # 服务管理
├── 📄 backup_recovery.py            # 备份恢复
├── 📄 system_monitor.py             # 系统监控
├── 📄 db_config_init.py             # 数据库初始化
├── 📄 install_test.py               # 安装测试
├── 📄 requirements.txt              # 依赖包列表
├── 📄 INSTALLATION_GUIDE.md         # 详细安装指南
│
├── 📁 config/                       # 配置文件目录
│   ├── config.ini                   # 主配置文件
│   ├── app_config.json              # 应用配置
│   ├── settings.py                  # 设置模块
│   └── theme.py                     # 主题配置
│
├── 📁 database/                     # 数据库相关
│   ├── manager.py                   # 数据库管理
│   ├── repositories.py              # 数据仓库
│   └── enhanced_initializer.py      # 数据库初始化
│
├── 📁 gui/                          # 图形界面
│   ├── base_components.py           # 基础组件
│   ├── table_components.py          # 表格组件
│   ├── analytics_charts_gui.py      # 图表界面
│   └── user_management_gui.py       # 用户管理
│
├── 📁 services/                     # 业务服务
│   ├── sales_service.py             # 销售服务
│   ├── inventory_service.py         # 库存服务
│   ├── member_service.py            # 会员服务
│   └── other_services.py            # 其他服务
│
├── 📁 security/                     # 安全模块
│   └── auth_module.py               # 认证授权
│
├── 📁 utils/                        # 工具模块
│   ├── system_utils.py              # 系统工具
│   ├── gui_utils.py                 # GUI工具
│   └── notification_utils.py        # 通知工具
│
├── 📁 data/                         # 数据存储
│   └── sisters_flowers_system.db    # SQLite数据库
│
├── 📁 logs/                         # 日志文件
│   ├── system.log                   # 系统日志
│   └── monitor.log                  # 监控日志
│
└── 📁 backup/                       # 备份目录
    └── [backup_files]               # 备份文件
```

## 🛠️ 管理工具

### 统一管理
- **图形界面**: `python system_manager.py --gui`
- **命令行**: `python system_manager.py --check`

### 备份恢复
- **创建备份**: `python backup_recovery.py backup --name backup_name`
- **恢复数据**: `python backup_recovery.py restore --backup-path ./backup/backup_name`
- **列出备份**: `python backup_recovery.py list`

### 系统监控
- **实时监控**: `python system_monitor.py monitor`
- **健康检查**: `python system_monitor.py check --health`
- **生成报告**: `python system_monitor.py report --type daily`

### 服务管理
- **安装服务**: `python service_manager.py install`
- **启动服务**: `python service_manager.py start`
- **查看状态**: `python service_manager.py status`

## 📊 功能模块

### 销售管理
- 🛒 **商品管理**: 商品信息录入，分类管理
- 📝 **销售开单**: 快速开单，支持多种付款方式
- 💰 **收银结算**: 自动计算，支持找零
- 📋 **销售查询**: 历史销售记录查询
- 📈 **销售统计**: 实时销售数据统计

### 库存管理
- 📦 **入库管理**: 采购入库，库存增加
- 📤 **出库管理**: 销售出库，库存减少
- ⚠️ **库存预警**: 低库存自动提醒
- 📊 **库存盘点**: 定期库存核对
- 📈 **库存分析**: 库存周转分析

### 客户管理
- 👤 **客户档案**: 客户基本信息维护
- 📞 **联系记录**: 客户联系历史
- 🎯 **客户分级**: VIP/普通客户管理
- 💳 **信用管理**: 客户信用额度
- 📊 **客户分析**: 客户价值分析

### 财务报表
- 💰 **销售日报**: 每日销售汇总
- 📊 **销售月报**: 月度经营分析
- 📈 **利润分析**: 毛利率分析
- 🏦 **收支明细**: 资金流水记录
- 📋 **财务报表**: 标准财务报表

### 数据分析
- 📈 **销售趋势**: 销售走势图表
- 🎯 **商品分析**: 商品销售排行
- 👥 **客户分析**: 客户行为分析
- 📊 **经营分析**: 经营状况评估
- 📋 **数据导出**: 多格式数据导出

## 🔧 系统配置

### 主配置文件
编辑 `config/app_config.json`:
```json
{
  "app": {
    "name": "姐妹花销售系统",
    "version": "4.0",
    "theme": "light"
  },
  "database": {
    "type": "sqlite",
    "backup_enabled": true
  },
  "ui": {
    "theme": "light",
    "window_size": "1200x800"
  }
}
```

### 数据库配置
- 默认使用SQLite数据库
- 支持MySQL和PostgreSQL（需配置）
- 自动备份和恢复功能

## 📋 系统要求

### 最低配置
- **操作系统**: Windows 10, Linux Ubuntu 18.04, macOS 10.14
- **Python**: 3.8 或更高版本
- **内存**: 2GB RAM
- **磁盘**: 500MB 可用空间

### 推荐配置
- **操作系统**: Windows 11, Linux Ubuntu 20.04, macOS 12
- **Python**: 3.9 或更高版本
- **内存**: 4GB RAM 或更多
- **磁盘**: 2GB 可用空间

## 🆘 故障排除

### 常见问题
1. **Python版本不兼容**: 升级到Python 3.8+
2. **依赖安装失败**: 使用国内镜像源
3. **GUI显示问题**: 安装系统tkinter支持
4. **数据库初始化失败**: 检查目录权限
5. **程序启动无响应**: 运行诊断工具

### 诊断工具
```bash
# 快速检查
python quick_start.py --check

# 故障诊断
python quick_start.py --diagnose

# 安装测试
python install_test.py
```

### 日志文件
- `logs/system.log` - 系统主日志
- `logs/monitor.log` - 监控日志
- `logs/backup.log` - 备份日志

## 📈 性能优化

### 系统优化建议
1. **定期清理**: 运行维护任务清理日志
2. **数据备份**: 设置自动备份策略
3. **性能监控**: 开启系统监控
4. **数据库优化**: 定期整理数据库

### 自动维护
```bash
# 手动维护
python system_monitor.py maintenance --cleanup --vacuum

# 设置定时任务（Linux）
crontab -e
0 2 * * * /usr/bin/python3 /path/to/system_monitor.py maintenance
```

## 🔐 安全建议

### 基础安全
1. **定期更新**: 保持系统最新版本
2. **强密码**: 使用复杂密码策略
3. **权限管理**: 合理分配用户权限
4. **数据备份**: 定期备份重要数据
5. **访问控制**: 限制系统访问权限

### 数据保护
- 敏感数据加密存储
- 用户操作完整记录
- 自动会话超时
- 失败登录锁定

## 🚀 更新升级

### 版本更新
```bash
# 检查更新
python system_manager.py --check

# 备份数据
python backup_recovery.py backup --name pre_update

# 应用更新
python install.py
```

### 数据迁移
```bash
# 导出数据
python backup_recovery.py backup --name migration_backup

# 导入数据
python backup_recovery.py restore --backup-path ./backup/migration_backup
```

## 📚 文档资源

- 📖 **[详细安装指南](INSTALLATION_GUIDE.md)** - 完整的安装和配置说明
- 👥 **用户手册** - 系统使用说明
- 🔧 **开发者文档** - API和技术文档
- 📹 **视频教程** - 快速入门视频
- ❓ **常见问题** - FAQ和解决方案

## 🤝 贡献指南

我们欢迎社区贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

### 贡献方式
- 🐛 **报告Bug**: 通过Issue报告问题
- 💡 **功能建议**: 提出新功能想法
- 📝 **代码贡献**: 提交Pull Request
- 📖 **文档改进**: 完善项目文档
- 🧪 **测试支持**: 参与测试和验证

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

- 核心开发团队
- 开源社区支持
- 测试用户反馈
- 技术文档贡献者

## 📞 联系我们

- **项目主页**: https://github.com/sisters-flowers/sales-system
- **问题反馈**: https://github.com/sisters-flowers/sales-system/issues
- **技术交流**: support@sisters-flowers.com
- **用户社区**: [QQ群: 123456789](https://qm.qq.com/cgi-bin/qm/qr?k=dummy-link)

---

<div align="center">

**🌸 姐妹花销售系统 - 让销售管理更简单 🌸**

*现代化销售管理解决方案*

[开始使用](quick_start.py) • [查看文档](INSTALLATION_GUIDE.md) • [获取支持](#-联系我们)

</div>