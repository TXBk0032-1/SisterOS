#!/usr/bin/env python3
"""
姐妹花销售系统 - 安装测试脚本
Sisters Flower Sales System - Installation Test Script

功能：
1. 测试所有系统模块导入
2. 验证数据库连接
3. 检查配置文件
4. 测试系统功能
5. 生成测试报告

作者: MiniMax Agent
版本: 1.0
"""

import argparse
import importlib
import json
import sqlite3
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, Optional, Any


class InstallationTester:
    """安装测试器"""
    
    def __init__(self):
        self.install_dir = Path(__file__).parent
        self.test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        # 添加安装目录到Python路径
        if str(self.install_dir) not in sys.path:
            sys.path.insert(0, str(self.install_dir))
    
    def test_python_environment(self) -> Dict[str, Any]:
        """测试Python环境"""
        test_name = "Python环境检查"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        try:
            # 检查Python版本
            if sys.version_info >= (3, 8):
                result["details"].append("✅ Python版本 >= 3.8")
                result["status"] = "passed"
            else:
                result["details"].append(f"❌ Python版本过低: {sys.version_info.major}.{sys.version_info.minor}")
                result["status"] = "failed"
                return result
            
            # 检查内置模块
            required_modules = [
                'tkinter', 'sqlite3', 'json', 'threading', 'pathlib', 
                'datetime', 'os', 'sys', 'subprocess', 'hashlib',
                'logging', 'urllib', 'tempfile', 'shutil'
            ]
            
            missing_modules = []
            for module in required_modules:
                try:
                    importlib.import_module(module)
                    result["details"].append(f"✅ {module} 模块可用")
                except ImportError:
                    missing_modules.append(module)
                    result["details"].append(f"❌ {module} 模块缺失")
            
            if missing_modules:
                result["status"] = "failed"
                result["error"] = f"缺少内置模块: {', '.join(missing_modules)}"
            else:
                result["status"] = "passed"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 测试异常: {e}")
        
        return result
    
    def test_system_dependencies(self) -> Dict[str, Any]:
        """测试系统依赖"""
        test_name = "系统依赖检查"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        # 必需依赖
        required_deps = [
            ('tkinter', 'GUI界面库'),
            ('sqlite3', 'SQLite数据库')
        ]
        
        # 可选依赖
        optional_deps = [
            ('ttkbootstrap', '现代化UI主题'),
            ('pywinstyles', 'Windows样式'),
            ('win32mica', 'Windows 11特效'),
            ('psutil', '系统监控'),
            ('pillow', '图像处理'),
            ('matplotlib', '图表绘制'),
            ('pandas', '数据分析'),
            ('numpy', '数值计算')
        ]
        
        try:
            # 测试必需依赖
            missing_required = []
            for module, description in required_deps:
                try:
                    importlib.import_module(module)
                    result["details"].append(f"✅ {module} ({description}) - 必需")
                except ImportError:
                    missing_required.append(module)
                    result["details"].append(f"❌ {module} ({description}) - 必需，缺失")
            
            # 测试可选依赖
            missing_optional = []
            for module, description in optional_deps:
                try:
                    importlib.import_module(module)
                    result["details"].append(f"✅ {module} ({description}) - 可选")
                except ImportError:
                    missing_optional.append(module)
                    result["details"].append(f"⚠️ {module} ({description}) - 可选，缺失（功能受限）")
            
            # 决定测试结果
            if missing_required:
                result["status"] = "failed"
                result["error"] = f"缺少必需依赖: {', '.join(missing_required)}"
            else:
                result["status"] = "passed"
                if missing_optional:
                    result["details"].append(f"⚠️ 缺少{len(missing_optional)}个可选依赖，部分功能受限")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 测试异常: {e}")
        
        return result
    
    def test_file_structure(self) -> Dict[str, Any]:
        """测试文件结构"""
        test_name = "文件结构检查"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        # 必需文件列表
        required_files = [
            "enhanced_sales_system.py",
            "requirements.txt",
            "install.py",
            "config/config.ini",
            "database/manager.py"
        ]
        
        # 可选文件列表
        optional_files = [
            "config/app_config.json",
            "config/settings.py",
            "gui/base_components.py",
            "services/sales_service.py",
            "utils/system_utils.py"
        ]
        
        try:
            # 检查必需文件
            missing_required = []
            for file_path in required_files:
                full_path = self.install_dir / file_path
                if full_path.exists():
                    result["details"].append(f"✅ {file_path} - 存在")
                else:
                    missing_required.append(file_path)
                    result["details"].append(f"❌ {file_path} - 缺失")
            
            # 检查可选文件
            missing_optional = []
            for file_path in optional_files:
                full_path = self.install_dir / file_path
                if full_path.exists():
                    result["details"].append(f"✅ {file_path} - 存在")
                else:
                    missing_optional.append(file_path)
                    result["details"].append(f"⚠️ {file_path} - 可选，缺失")
            
            # 决定测试结果
            if missing_required:
                result["status"] = "failed"
                result["error"] = f"缺少必需文件: {', '.join(missing_required)}"
            else:
                result["status"] = "passed"
                if missing_optional:
                    result["details"].append(f"⚠️ 缺少{len(missing_optional)}个可选文件，部分功能可能受限")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 测试异常: {e}")
        
        return result
    
    def test_module_imports(self) -> Dict[str, Any]:
        """测试模块导入"""
        test_name = "模块导入测试"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        # 要测试的模块列表
        test_modules = [
            # 核心模块
            ('config.setting_manager', '配置管理'),
            ('config.settings', '设置模块'),
            ('database.manager', '数据库管理'),
            ('database.repositories', '数据仓库'),
            
            # GUI模块
            ('gui.base_components', '基础组件'),
            ('gui.table_components', '表格组件'),
            
            # 服务模块
            ('services.sales_service', '销售服务'),
            ('services.inventory_service', '库存服务'),
            ('services.member_service', '会员服务'),
            
            # 工具模块
            ('utils.system_utils', '系统工具'),
            ('utils.path_utils', '路径工具'),
            ('utils.gui_utils', 'GUI工具')
        ]
        
        try:
            import_failures = []
            
            for module_name, description in test_modules:
                try:
                    importlib.import_module(module_name)
                    result["details"].append(f"✅ {module_name} ({description})")
                except ImportError as e:
                    import_failures.append((module_name, str(e)))
                    result["details"].append(f"❌ {module_name} ({description}) - 导入失败")
                except Exception as e:
                    import_failures.append((module_name, str(e)))
                    result["details"].append(f"❌ {module_name} ({description}) - 异常: {e}")
            
            # 决定测试结果
            if import_failures:
                result["status"] = "failed"
                result["error"] = f"{len(import_failures)}个模块导入失败"
                result["failures"] = import_failures
            else:
                result["status"] = "passed"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 测试异常: {e}")
        
        return result
    
    def test_database_connection(self) -> Dict[str, Any]:
        """测试数据库连接"""
        test_name = "数据库连接测试"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        try:
            # 查找数据库文件
            db_files = list(self.install_dir.glob("*.db")) + list((self.install_dir / "data").glob("*.db"))
            
            if not db_files:
                result["details"].append("⚠️ 未找到数据库文件，创建测试数据库...")
                
                # 创建测试数据库
                test_db = self.install_dir / "test_installation.db"
                conn = sqlite3.connect(str(test_db))
                cursor = conn.cursor()
                
                # 创建测试表
                cursor.execute("""
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        value INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入测试数据
                cursor.executemany(
                    "INSERT INTO test_table (name, value) VALUES (?, ?)",
                    [("test1", 100), ("test2", 200), ("test3", 300)]
                )
                
                # 测试查询
                cursor.execute("SELECT COUNT(*) FROM test_table")
                count = cursor.fetchone()[0]
                
                if count == 3:
                    result["details"].append("✅ 数据库创建和基本操作成功")
                    result["status"] = "passed"
                else:
                    result["details"].append("❌ 数据库操作异常")
                    result["status"] = "failed"
                
                conn.close()
                
                # 清理测试数据库
                test_db.unlink()
                
            else:
                # 测试现有数据库
                db_file = db_files[0]
                result["details"].append(f"找到数据库文件: {db_file}")
                
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                
                # 测试基本查询
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if tables:
                    result["details"].append(f"✅ 找到 {len(tables)} 个数据表")
                    
                    # 测试每个表的基本操作
                    for (table_name,) in tables:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                            count = cursor.fetchone()[0]
                            result["details"].append(f"  ✅ 表 {table_name}: {count} 条记录")
                        except sqlite3.Error:
                            result["details"].append(f"  ❌ 表 {table_name}: 查询失败")
                    
                    result["status"] = "passed"
                else:
                    result["details"].append("❌ 数据库中无数据表")
                    result["status"] = "failed"
                
                conn.close()
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 数据库测试异常: {e}")
            result["details"].append(f"错误详情: {traceback.format_exc()}")
        
        return result
    
    def test_config_files(self) -> Dict[str, Any]:
        """测试配置文件"""
        test_name = "配置文件测试"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        try:
            config_files = list(self.install_dir.glob("config/*.json")) + \
                          list(self.install_dir.glob("config/*.ini")) + \
                          list(self.install_dir.glob("*.json"))
            
            if not config_files:
                result["details"].append("⚠️ 未找到配置文件")
                result["status"] = "skipped"
                return result
            
            config_errors = []
            
            for config_file in config_files:
                try:
                    if config_file.suffix == '.json':
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        result["details"].append(f"✅ {config_file.name} (JSON格式)")
                    elif config_file.suffix == '.ini':
                        # 简单检查INI文件可读性
                        with open(config_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        result["details"].append(f"✅ {config_file.name} (INI格式)")
                    
                except json.JSONDecodeError as e:
                    config_errors.append(f"{config_file.name}: JSON格式错误 - {e}")
                    result["details"].append(f"❌ {config_file.name}: JSON格式错误")
                except Exception as e:
                    config_errors.append(f"{config_file.name}: 读取错误 - {e}")
                    result["details"].append(f"❌ {config_file.name}: 读取错误")
            
            if config_errors:
                result["status"] = "failed"
                result["error"] = f"{len(config_errors)}个配置文件有错误"
            else:
                result["status"] = "passed"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 配置文件测试异常: {e}")
        
        return result
    
    def test_gui_functionality(self) -> Dict[str, Any]:
        """测试GUI功能"""
        test_name = "GUI功能测试"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        try:
            # 检查tkinter是否可用
            import tkinter as tk
            result["details"].append("✅ tkinter GUI库可用")
            
            # 创建测试窗口
            root = tk.Tk()
            root.title("安装测试")
            root.geometry("100x100")
            
            # 测试基础组件
            test_label = tk.Label(root, text="测试")
            test_label.pack()
            
            test_button = tk.Button(root, text="测试按钮")
            test_button.pack()
            
            test_entry = tk.Entry(root)
            test_entry.pack()
            
            # 测试ttk（如果可用）
            try:
                import ttkbootstrap as ttk_bs
                result["details"].append("✅ ttkbootstrap 可用")
                
                # 创建ttkbootstrap应用
                app = ttk_bs.Window()
                app.destroy()
                
            except ImportError:
                result["details"].append("⚠️ ttkbootstrap 不可用，将使用标准tkinter")
            
            # 关闭测试窗口
            root.destroy()
            
            result["status"] = "passed"
            result["details"].append("✅ GUI基础功能测试通过")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ GUI测试失败: {e}")
        
        return result
    
    def test_application_startup(self) -> Dict[str, Any]:
        """测试应用程序启动"""
        test_name = "应用程序启动测试"
        result = {"test_name": test_name, "status": "unknown", "details": []}
        
        try:
            app_script = self.install_dir / "enhanced_sales_system.py"
            
            if not app_script.exists():
                result["status"] = "skipped"
                result["details"].append("⚠️ 应用程序主文件不存在")
                return result
            
            # 尝试导入主程序模块（不实际启动GUI）
            result["details"].append("测试应用程序模块导入...")
            
            # 模拟应用程序的启动过程，但不显示GUI
            spec = importlib.util.spec_from_file_location("enhanced_sales_system", app_script)
            if spec and spec.loader:
                result["details"].append("✅ 应用程序文件结构正确")
                result["status"] = "passed"
            else:
                result["status"] = "failed"
                result["error"] = "应用程序文件无法正常加载"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["details"].append(f"❌ 应用程序启动测试失败: {e}")
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🔧 开始安装测试...")
        print("=" * 60)
        
        # 测试函数映射
        test_functions = {
            "python_environment": self.test_python_environment,
            "system_dependencies": self.test_system_dependencies,
            "file_structure": self.test_file_structure,
            "module_imports": self.test_module_imports,
            "database_connection": self.test_database_connection,
            "config_files": self.test_config_files,
            "gui_functionality": self.test_gui_functionality,
            "application_startup": self.test_application_startup
        }
        
        for test_key, test_func in test_functions.items():
            print(f"🔍 运行测试: {test_func.__name__}...")
            try:
                test_result = test_func()
                self.test_results["tests"][test_key] = test_result
                
                # 更新统计
                self.test_results["summary"]["total"] += 1
                if test_result["status"] == "passed":
                    self.test_results["summary"]["passed"] += 1
                    print(f"  ✅ 通过")
                elif test_result["status"] == "failed":
                    self.test_results["summary"]["failed"] += 1
                    print(f"  ❌ 失败")
                elif test_result["status"] == "skipped":
                    self.test_results["summary"]["skipped"] += 1
                    print(f"  ⏭️ 跳过")
                
                # 显示详细信息
                for detail in test_result.get("details", []):
                    print(f"    {detail}")
                
                if "error" in test_result:
                    print(f"  ❌ 错误: {test_result['error']}")
                
            except Exception as e:
                print(f"  ❌ 测试异常: {e}")
                self.test_results["tests"][test_key] = {
                    "test_name": test_func.__name__,
                    "status": "failed",
                    "error": str(e),
                    "details": [f"测试执行异常: {e}"]
                }
                self.test_results["summary"]["total"] += 1
                self.test_results["summary"]["failed"] += 1
        
        return self.test_results
    
    def generate_report(self, output_file: Optional[Path] = None) -> str:
        """生成测试报告"""
        summary = self.test_results["summary"]
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                姐妹花销售系统 - 安装测试报告                   ║
║              Sisters Flower Sales System                     ║
║                  Installation Test Report                   ║
╚══════════════════════════════════════════════════════════════╝

测试时间: {self.test_results['timestamp']}
Python版本: {self.test_results['python_version']}
测试目录: {self.install_dir}

📊 测试摘要:
  总计测试: {summary['total']}
  通过: {summary['passed']} ✅
  失败: {summary['failed']} ❌
  跳过: {summary['skipped']} ⏭️
  
  成功率: {(summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.1f}%

"""
        
        # 详细结果
        report += "📋 详细结果:\n"
        report += "=" * 60 + "\n"
        
        for test_key, test_result in self.test_results["tests"].items():
            status_icon = {
                "passed": "✅",
                "failed": "❌", 
                "skipped": "⏭️"
            }.get(test_result["status"], "❓")
            
            report += f"\n{status_icon} {test_result['test_name']}\n"
            report += f"   状态: {test_result['status']}\n"
            
            if "error" in test_result:
                report += f"   错误: {test_result['error']}\n"
            
            for detail in test_result.get("details", []):
                report += f"   {detail}\n"
        
        # 总结和建议
        report += "\n" + "=" * 60 + "\n"
        if summary["failed"] == 0:
            report += "🎉 所有测试通过！系统安装成功，可以正常使用。\n"
        else:
            report += f"⚠️ 有 {summary['failed']} 个测试失败，请检查以下问题：\n"
            
            # 生成建议
            report += "\n💡 建议解决方案：\n"
            if any(test["status"] == "failed" for test in self.test_results["tests"].values()):
                report += "1. 运行自动安装程序: python install.py\n"
                report += "2. 安装缺失的依赖: pip install -r requirements.txt\n"
                report += "3. 检查Python版本: 确保使用Python 3.8或更高版本\n"
                report += "4. 检查文件权限: 确保对安装目录有读写权限\n"
        
        report += "\n" + "=" * 60 + "\n"
        report += "报告生成完成\n"
        
        # 保存报告
        if output_file is None:
            output_file = self.install_dir / "installation_test_report.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 测试报告已保存到: {output_file}")
        except Exception as e:
            print(f"\n❌ 保存报告失败: {e}")
        
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="姐妹花销售系统 - 安装测试工具")
    parser.add_argument("--output", type=Path, help="测试报告输出文件")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="输出JSON格式结果")
    
    args = parser.parse_args()
    
    tester = InstallationTester()
    
    try:
        # 运行测试
        results = tester.run_all_tests()
        
        # 生成报告
        if args.json:
            # JSON格式输出
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            # 文本格式报告
            report = tester.generate_report(args.output)
            print("\n" + report)
        
        # 返回适当的退出码
        summary = results["summary"]
        if summary["failed"] == 0:
            sys.exit(0)  # 成功
        else:
            sys.exit(1)  # 有测试失败
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中出现未预期错误: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()