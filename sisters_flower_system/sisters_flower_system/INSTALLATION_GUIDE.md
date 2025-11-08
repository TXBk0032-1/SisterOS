# 姐妹花销售系统 v4.0 - 完整安装指南

## 📋 目录
1. [系统要求](#系统要求)
2. [快速安装](#快速安装)
3. [详细安装](#详细安装)
4. [配置说明](#配置说明)
5. [常见问题](#常见问题)
6. [故障排除](#故障排除)
7. [卸载说明](#卸载说明)

---

## 💻 系统要求

### 最低要求
- **操作系统**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python版本**: 3.8 或更高版本
- **内存**: 2GB RAM（推荐 4GB+）
- **磁盘空间**: 500MB 可用空间
- **显示器**: 1024x768 分辨率

### 推荐配置
- **操作系统**: Windows 11, Linux (Ubuntu 20.04+), macOS 12+
- **Python版本**: 3.9 或更高版本
- **内存**: 4GB RAM 或更多
- **磁盘空间**: 2GB 可用空间
- **显示器**: 1920x1080 分辨率

### 依赖软件
- **Python 3.8+** - [下载地址](https://www.python.org/downloads/)
- **pip** - Python 包管理器（通常随Python一起安装）

---

## 🚀 快速安装

### Windows 用户
1. **下载系统文件**
   ```bash
   # 确保已下载所有系统文件到本地目录
   cd sisters_flower_system
   ```

2. **运行自动安装**
   ```cmd
   # 双击运行
   install_windows.bat
   
   # 或命令行运行
   python install.py
   ```

3. **启动系统**
   ```cmd
   # 启动应用程序
   python enhanced_sales_system.py
   
   # 或使用快速启动
   python quick_start.py
   ```

### Linux/macOS 用户
1. **设置执行权限**
   ```bash
   chmod +x install_linux.sh
   ```

2. **运行安装脚本**
   ```bash
   # 交互式安装
   ./install_linux.sh
   
   # 静默安装
   ./install_linux.sh --skip-full-install
   ```

3. **启动系统**
   ```bash
   # 使用启动脚本
   ./launch_sales_system.sh
   
   # 或直接运行
   python3 enhanced_sales_system.py
   ```

### 统一快速启动
```bash
# 快速检查和启动
python quick_start.py

# 系统检查
python quick_start.py --check

# 故障诊断
python quick_start.py --diagnose
```

---

## 🔧 详细安装

### 第一步：检查Python环境
```bash
# 检查Python版本
python --version
# 或
python3 --version

# 检查pip
pip --version
# 或
pip3 --version
```

### 第二步：安装依赖
```bash
# 升级pip
python -m pip install --upgrade pip

# 安装依赖包
pip install -r requirements.txt

# 可选：安装额外功能包
pip install psutil matplotlib pandas
```

### 第三步：初始化数据库
```bash
# 初始化数据库
python db_config_init.py init-db --db-path ./data/sisters_flowers_system.db --config-dir ./config

# 创建配置文件
python db_config_init.py init-config --config-dir ./config
```

### 第四步：运行系统测试
```bash
# 运行完整测试
python install_test.py

# 生成测试报告
python install_test.py --output test_report.txt
```

### 第五步：启动应用
```bash
# 启动主程序
python enhanced_sales_system.py

# 或使用管理工具
python system_manager.py --gui
```

---

## ⚙️ 配置说明

### 主要配置文件
- `config/app_config.json` - 主配置文件
- `config/settings.py` - 应用程序设置
- `config/config.ini` - 系统配置
- `data/sisters_flowers_system.db` - SQLite数据库

### 配置选项说明
```json
{
  "app": {
    "name": "姐妹花销售系统",
    "version": "4.0",
    "theme": "light"
  },
  "database": {
    "type": "sqlite",
    "backup_enabled": true,
    "backup_interval_hours": 24
  },
  "ui": {
    "theme": "light",
    "window_size": "1200x800"
  },
  "security": {
    "session_timeout_minutes": 60,
    "max_login_attempts": 3
  }
}
```

### 环境变量
创建 `.env` 文件（可选）：
```bash
# 系统配置
APP_ENV=production
LOG_LEVEL=INFO

# 数据库配置
DB_PATH=./data/sisters_flowers_system.db

# 备份配置
BACKUP_DIR=./backup
BACKUP_RETENTION_DAYS=30
```

---

## 🔧 系统管理工具

### 统一管理工具
```bash
# 启动图形化管理界面
python system_manager.py --gui

# 命令行模式
python system_manager.py --check
python system_manager.py --install
python system_manager.py --status
```

### 备份和恢复
```bash
# 创建备份
python backup_recovery.py backup --name manual_backup_20241201

# 列出备份
python backup_recovery.py list

# 恢复备份
python backup_recovery.py restore --backup-path ./backup/manual_backup_20241201

# 交互式恢复
python backup_recovery.py restore --interactive
```

### 系统监控
```bash
# 启动监控服务
python system_monitor.py monitor

# 单次检查
python system_monitor.py check --health

# 生成报告
python system_monitor.py report --type daily
```

### 服务管理
```bash
# 安装系统服务
python service_manager.py install

# 启动/停止服务
python service_manager.py start
python service_manager.py stop

# 查看服务状态
python service_manager.py status
```

---

## ❓ 常见问题

### Q1: Python版本不兼容
**问题**: "Python 3.8 or higher is required"
**解决**:
```bash
# 检查当前版本
python --version

# 如版本过低，请升级Python
# Windows: 从官网下载新版Python安装
# Linux: sudo apt install python3.9
# macOS: brew install python@3.9
```

### Q2: 依赖包安装失败
**问题**: "pip install failed"
**解决**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 逐个安装依赖
pip install tkinter  # 通常内置
pip install ttkbootstrap
pip install pillow
```

### Q3: GUI显示问题
**问题**: "tkinter not found" 或界面显示异常
**解决**:
```bash
# Linux下安装tkinter
sudo apt-get install python3-tk

# 检查显示器设置
export DISPLAY=:0  # Linux图形界面

# 如果在服务器环境，使用Xvfb
sudo apt-get install xvfb
Xvfb :99 -ac -screen 0 1024x768x16 &
export DISPLAY=:99
```

### Q4: 数据库初始化失败
**问题**: "Database initialization failed"
**解决**:
```bash
# 检查目录权限
ls -la data/
chmod 755 data/

# 手动初始化数据库
python db_config_init.py init-db --db-path ./data/sisters_flowers_system.db --config-dir ./config --no-sample-data

# 检查磁盘空间
df -h
```

### Q5: 启动程序无响应
**问题**: 程序启动后卡住或无界面显示
**解决**:
```bash
# 运行诊断
python quick_start.py --diagnose

# 查看错误日志
tail -f logs/system.log

# 以调试模式启动
python enhanced_sales_system.py --debug

# 检查进程冲突
ps aux | grep enhanced_sales_system
```

---

## 🚨 故障排除

### 诊断工具
```bash
# 快速系统检查
python quick_start.py --check

# 完整诊断报告
python quick_start.py --diagnose

# 安装测试
python install_test.py --verbose
```

### 日志文件位置
- `logs/system.log` - 系统主日志
- `logs/monitor.log` - 监控日志
- `logs/backup.log` - 备份日志
- `logs/service.log` - 服务日志

### 重置系统
```bash
# 备份数据
python backup_recovery.py backup --name pre_reset

# 重置配置
rm config/app_config.json
python db_config_init.py init-config --config-dir ./config

# 重新初始化
python install.py
```

### 完全重装
```bash
# 停止所有相关进程
python service_manager.py stop

# 备份重要数据
python backup_recovery.py backup --name pre_reinstall

# 清理安装
rm -rf config/ data/ logs/ backup/
# Windows: rmdir /s config data logs backup

# 重新安装
python install.py
```

---

## 🗑️ 卸载说明

### 完全卸载
```bash
# 1. 停止系统服务
python service_manager.py stop
python service_manager.py uninstall

# 2. 备份重要数据（可选）
python backup_recovery.py backup --name final_backup

# 3. 删除系统文件
rm -rf sisters_flower_system/
# Windows: 删除整个sisters_flower_system文件夹

# 4. 卸载Python依赖（可选）
pip uninstall -r requirements.txt
```

### 保留数据卸载
如果只想卸载程序但保留数据：
```bash
# 停止服务
python service_manager.py stop

# 删除程序文件，保留data目录
# 手动删除除data/外的所有文件

# 重新安装时指定现有数据目录
python install.py --data-dir ./existing_data
```

---

## 📞 技术支持

### 获取帮助
- 📧 技术支持邮箱: support@sisters-flowers.com
- 📱 用户交流群: QQ群 123456789
- 🐛 问题报告: GitHub Issues
- 📖 在线文档: https://docs.sisters-flowers.com

### 报告问题时请提供
1. 操作系统信息 (`python quick_start.py --info`)
2. 错误日志 (`logs/system.log`)
3. 复现步骤
4. 预期结果 vs 实际结果

### 社区资源
- 官方文档: [docs.sisters-flowers.com](https://docs.sisters-flowers.com)
- 视频教程: [bilibili.com/sisters-flowers](https://bilibili.com/sisters-flowers)
- 常见问题: [FAQ](https://faq.sisters-flowers.com)

---

## 📄 许可证信息

**姐妹花销售系统 v4.0**
- 版权 © 2024 姐妹花科技有限公司
- 许可证: MIT License
- 第三方依赖: 详见 `requirements.txt`

---

*最后更新: 2024年12月*