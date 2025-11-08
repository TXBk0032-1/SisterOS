@echo off
chcp 65001 > nul
echo ======================================================
echo 🌸 姐妹花销售系统 - Windows 安装脚本 🌸
echo    Sisters Flower Sales System - Windows Installer
echo ======================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Python 未安装或未添加到系统PATH
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 显示Python版本
echo ✅ 检测到Python版本:
python --version
echo.

:: 检查Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 🔍 使用Python版本: %PYTHON_VERSION%
echo.

:: 检查pip
echo 🔍 检查pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: pip 不可用
    echo 尝试重新安装Python或修复pip
    pause
    exit /b 1
)

:: 升级pip
echo 🔄 升级pip到最新版本...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ pip升级失败，但继续安装...
)

:: 安装依赖
echo.
echo 📦 安装依赖包...
echo 这可能需要几分钟时间，请耐心等待...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败
    echo 请检查网络连接或手动安装依赖
    pause
    exit /b 1
)

echo ✅ 依赖包安装完成

:: 询问是否运行完整安装
echo.
set /p RUN_FULL_INSTALL="是否运行完整安装配置? (Y/n): "
if /i "%RUN_FULL_INSTALL%"=="Y" (
    echo 🚀 启动完整安装程序...
    python install.py
) else (
    echo ⏭️ 跳过完整安装配置
    echo 请稍后手动运行: python install.py
)

echo.
echo ======================================================
echo 🎉 安装脚本执行完成！
echo ======================================================
echo.
echo 📋 后续步骤:
echo 1. 如需完整配置，请运行: python install.py
echo 2. 启动系统: python enhanced_sales_system.py
echo 3. 查看帮助: 打开 README.md 文件
echo.
pause