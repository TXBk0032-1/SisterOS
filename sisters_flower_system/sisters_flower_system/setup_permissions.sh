#!/bin/bash
# 姐妹花销售系统 - 权限设置脚本
# Sisters Flower Sales System - Permission Setup Script

echo "🌸 设置姐妹花销售系统文件权限..."
echo "========================================"

# 获取当前目录
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📍 设置目录: $CURRENT_DIR"

# 设置目录权限
echo "📁 设置目录权限..."
chmod 755 "$CURRENT_DIR"
chmod 755 "$CURRENT_DIR/config" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/database" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/gui" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/services" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/security" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/utils" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/data" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/logs" 2>/dev/null || true
chmod 755 "$CURRENT_DIR/backup" 2>/dev/null || true

echo "✅ 目录权限设置完成"

# 设置Python脚本执行权限
echo "🐍 设置Python脚本权限..."
chmod +x "$CURRENT_DIR"/*.py 2>/dev/null || true

# 设置特定工具的权限
TOOLS=(
    "install_linux.sh"
    "launch_sales_system.sh"
    "quick_start.py"
    "install.py"
    "system_manager.py"
    "service_manager.py"
    "backup_recovery.py"
    "system_monitor.py"
    "db_config_init.py"
    "install_test.py"
)

for tool in "${TOOLS[@]}"; do
    if [ -f "$CURRENT_DIR/$tool" ]; then
        chmod +x "$CURRENT_DIR/$tool"
        echo "  ✅ $tool"
    fi
done

echo "✅ Python脚本权限设置完成"

# 设置配置文件权限
echo "⚙️ 设置配置文件权限..."
find "$CURRENT_DIR" -name "*.json" -exec chmod 644 {} \; 2>/dev/null || true
find "$CURRENT_DIR" -name "*.ini" -exec chmod 644 {} \; 2>/dev/null || true
find "$CURRENT_DIR" -name "*.cfg" -exec chmod 644 {} \; 2>/dev/null || true
find "$CURRENT_DIR" -name "*.txt" -exec chmod 644 {} \; 2>/dev/null || true
find "$CURRENT_DIR" -name "*.md" -exec chmod 644 {} \; 2>/dev/null || true

echo "✅ 配置文件权限设置完成"

# 设置数据文件权限
echo "💾 设置数据文件权限..."
find "$CURRENT_DIR/data" -type d -exec chmod 755 {} \; 2>/dev/null || true
find "$CURRENT_DIR/data" -type f -exec chmod 644 {} \; 2>/dev/null || true

# 设置日志文件权限
echo "📋 设置日志文件权限..."
find "$CURRENT_DIR/logs" -type d -exec chmod 755 {} \; 2>/dev/null || true
find "$CURRENT_DIR/logs" -type f -exec chmod 644 {} \; 2>/dev/null || true

# 设置备份目录权限
echo "💾 设置备份目录权限..."
find "$CURRENT_DIR/backup" -type d -exec chmod 755 {} \; 2>/dev/null || true
find "$CURRENT_DIR/backup" -type f -exec chmod 644 {} \; 2>/dev/null || true

echo "✅ 数据文件权限设置完成"

# 验证权限设置
echo ""
echo "🔍 验证权限设置..."

# 检查关键文件权限
CRITICAL_FILES=(
    "enhanced_sales_system.py"
    "install.py"
    "quick_start.py"
    "requirements.txt"
)

all_ok=true
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$CURRENT_DIR/$file" ]; then
        if [ -x "$CURRENT_DIR/$file" ] || [[ "$file" == "requirements.txt" ]]; then
            echo "  ✅ $file - 权限正确"
        else
            echo "  ❌ $file - 权限错误"
            all_ok=false
        fi
    else
        echo "  ⚠️ $file - 文件不存在"
    fi
done

# 显示目录权限摘要
echo ""
echo "📊 权限设置摘要:"
echo "  目录权限: 755 (rwxr-xr-x)"
echo "  Python文件: +x (可执行)"
echo "  配置文件: 644 (rw-r--r--)"
echo "  数据文件: 644 (rw-r--r--)"

# 最终确认
echo ""
if [ "$all_ok" = true ]; then
    echo "🎉 权限设置完成！系统已准备就绪。"
    echo ""
    echo "🚀 快速启动:"
    echo "  python quick_start.py"
    echo ""
    echo "📖 更多信息:"
    echo "  README.md - 项目说明"
    echo "  INSTALLATION_GUIDE.md - 详细安装指南"
    echo "  DEPLOYMENT_GUIDE.md - 部署包使用指南"
else
    echo "⚠️  部分文件权限设置有问题，请检查并手动修复。"
fi

echo "========================================"
echo "🌸 权限设置脚本执行完成"