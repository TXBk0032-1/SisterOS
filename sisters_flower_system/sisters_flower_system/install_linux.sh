#!/bin/bash
# 姐妹花销售系统 - Linux/Mac 安装脚本
# Sisters Flower Sales System - Linux/Mac Installer

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}======================================================${NC}"
    echo -e "${PURPLE}🌸 姐妹花销售系统 - Linux/Mac 安装脚本 🌸${NC}"
    echo -e "${PURPLE}   Sisters Flower Sales System - Linux/Mac Installer${NC}"
    echo -e "${PURPLE}======================================================${NC}"
    echo
}

# 检查依赖函数
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        print_info "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        print_info "CentOS/RHEL: sudo yum install python3 python3-pip"
        print_info "macOS: brew install python3"
        exit 1
    fi
    
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "检测到Python版本: $python_version"
    
    # 检查版本
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "需要Python 3.8或更高版本"
        exit 1
    fi
    
    # 检查pip
    if ! python3 -m pip --version &> /dev/null; then
        print_info "安装pip..."
        python3 -m ensurepip --upgrade || {
            print_error "pip安装失败"
            exit 1
        }
    fi
    
    print_success "系统依赖检查完成"
}

# 安装Python依赖
install_dependencies() {
    print_info "升级pip..."
    python3 -m pip install --upgrade pip --user
    
    print_info "安装Python依赖包..."
    print_warning "这可能需要几分钟时间，请耐心等待..."
    
    if python3 -m pip install -r requirements.txt --user; then
        print_success "依赖包安装完成"
    else
        print_error "依赖包安装失败"
        print_info "请检查网络连接或手动安装依赖"
        exit 1
    fi
}

# 创建必要目录
create_directories() {
    print_info "创建目录结构..."
    
    local dirs=(
        "data"
        "logs" 
        "backup"
        "config/themes"
        "config/exports"
        "config/temp"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        print_success "创建目录: $dir"
    done
}

# 设置执行权限
set_permissions() {
    print_info "设置文件权限..."
    
    # 使Python脚本可执行
    find . -name "*.py" -exec chmod +x {} \;
    print_success "设置Python脚本权限"
    
    # 设置目录权限
    chmod 755 .
    chmod 755 config/ data/ logs/ backup/ 2>/dev/null || true
    print_success "设置目录权限"
}

# 创建启动脚本
create_launcher() {
    print_info "创建启动脚本..."
    
    # 创建Linux启动脚本
    cat > launch_sales_system.sh << 'EOF'
#!/bin/bash
# 姐妹花销售系统启动脚本

cd "$(dirname "$0")"
python3 enhanced_sales_system.py
EOF
    
    chmod +x launch_sales_system.sh
    print_success "创建启动脚本: launch_sales_system.sh"
    
    # 创建桌面快捷方式（如果在桌面环境）
    if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
        print_info "创建桌面快捷方式..."
        
        local desktop_file="$HOME/Desktop/sisters-flower-system.desktop"
        cat > "$desktop_file" << EOF
[Desktop Entry]
Name=姐妹花销售系统
Name[en]=Sisters Flower Sales System
Comment=现代化销售管理系统
Comment[en]=Modern Sales Management System
Exec=$(pwd)/launch_sales_system.sh
Icon=applications-office
Terminal=false
Type=Application
Categories=Office;
StartupNotify=true
EOF
        
        chmod +x "$desktop_file"
        print_success "创建桌面快捷方式"
    fi
}

# 运行安装测试
run_installation_test() {
    print_info "运行安装测试..."
    
    if python3 -c "
import sys
import importlib.util
import os

# 测试关键模块导入
test_modules = [
    'tkinter',
    'sqlite3', 
    'json',
    'datetime',
    'pathlib',
    'config.setting_manager',
    'config.settings',
    'database.manager'
]

failed_modules = []
for module in test_modules:
    try:
        if '.' in module:
            spec = importlib.util.find_spec(module)
            if spec is None:
                failed_modules.append(module)
        else:
            __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        failed_modules.append(module)
        print(f'❌ {module}: {e}')

if failed_modules:
    print(f'❌ 以下模块导入失败: {failed_modules}')
    sys.exit(1)
else:
    print('✅ 所有核心模块测试通过')
" 2>/dev/null; then
        print_success "安装测试通过"
    else
        print_warning "部分功能可能受限，但基本功能可用"
    fi
}

# 显示完成信息
show_completion_message() {
    echo
    echo -e "${GREEN}======================================================${NC}"
    echo -e "${GREEN}🎉 安装完成！${NC}"
    echo -e "${GREEN}======================================================${NC}"
    echo
    echo -e "${CYAN}📋 安装信息:${NC}"
    echo -e "  📁 安装目录: $(pwd)"
    echo -e "  🐍 Python版本: $(python3 --version)"
    echo
    echo -e "${CYAN}🚀 启动方式:${NC}"
    echo -e "  1. 运行启动脚本: ./launch_sales_system.sh"
    echo -e "  2. 直接运行: python3 enhanced_sales_system.py"
    echo -e "  3. 完整配置: python3 install.py"
    echo
    echo -e "${CYAN}📖 更多信息:${NC}"
    echo -e "  • 用户手册: README.md"
    echo -e "  • 配置说明: config/app_config.json"
    echo -e "  • 日志文件: logs/"
    echo
    echo -e "${YELLOW}💡 提示:${NC}"
    echo -e "  • 如需完整功能配置，请运行: python3 install.py"
    echo -e "  • 如遇问题请查看 logs/system.log"
    echo
    echo -e "${GREEN}======================================================${NC}"
}

# 主函数
main() {
    print_header
    
    # 解析命令行参数
    SKIP_FULL_INSTALL=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-full-install)
                SKIP_FULL_INSTALL=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --skip-full-install    跳过完整安装配置"
                echo "  --help, -h             显示帮助信息"
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行安装步骤
    check_dependencies
    install_dependencies  
    create_directories
    set_permissions
    create_launcher
    run_installation_test
    
    # 询问是否运行完整安装
    if [ "$SKIP_FULL_INSTALL" = false ]; then
        echo
        read -p "是否运行完整安装配置? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            print_info "启动完整安装程序..."
            python3 install.py
        else
            print_info "跳过完整安装配置"
            print_info "请稍后手动运行: python3 install.py"
        fi
    fi
    
    show_completion_message
}

# 执行主函数
main "$@"