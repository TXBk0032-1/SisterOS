#!/usr/bin/env python3
"""
姐妹花销售系统 - 快速性能基准测试
Quick Performance Benchmark for Sisters Flower System

专注于性能测试，不依赖GUI组件
"""

import sys
import os
import time
import sqlite3
import tempfile
import shutil
import json
from datetime import datetime
from unittest.mock import Mock

# 添加系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_test_db():
    """设置测试数据库"""
    temp_dir = tempfile.mkdtemp(prefix="perf_test_")
    db_path = os.path.join(temp_dir, "perf_test.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表结构
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            barcode TEXT,
            category TEXT,
            price REAL,
            cost REAL,
            stock INTEGER,
            alert_threshold INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            sale_date DATE,
            total_amount REAL,
            member_id INTEGER
        )
    """)
    
    return conn, temp_dir, db_path

def benchmark_database_operations():
    """基准测试数据库操作"""
    print("🗄️  数据库性能基准测试")
    print("=" * 50)
    
    conn, temp_dir, db_path = setup_test_db()
    cursor = conn.cursor()
    
    # 测试1: 批量插入
    print("📊 测试1: 批量插入性能")
    start_time = time.time()
    
    test_data = []
    for i in range(10000):
        test_data.append((
            f"产品{i:05d}",
            f"BC{i:012d}",
            f"类别{i%10}",
            100.0 + i,
            80.0 + i,
            50 + (i % 100),
            10
        ))
    
    cursor.executemany("""
        INSERT INTO products (name, barcode, category, price, cost, stock, alert_threshold)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, test_data)
    conn.commit()
    
    insert_time = time.time() - start_time
    print(f"  ✅ 插入10000条记录: {insert_time:.3f}秒 ({10000/insert_time:.0f} 记录/秒)")
    
    # 测试2: 复杂查询
    print("📊 测试2: 查询性能")
    start_time = time.time()
    
    for _ in range(1000):
        cursor.execute("""
            SELECT p.name, p.category, p.price, p.stock
            FROM products p
            WHERE p.category LIKE '类别%'
            AND p.stock <= p.alert_threshold
            AND p.price > 100
            ORDER BY p.price DESC
            LIMIT 20
        """)
        results = cursor.fetchall()
    
    query_time = time.time() - start_time
    print(f"  ✅ 1000次复杂查询: {query_time:.3f}秒 ({query_time/1000*1000:.1f}ms/查询)")
    
    # 测试3: 聚合查询
    print("📊 测试3: 聚合查询性能")
    start_time = time.time()
    
    for _ in range(100):
        cursor.execute("""
            SELECT 
                category,
                COUNT(*) as product_count,
                AVG(price) as avg_price,
                SUM(stock * cost) as total_value
            FROM products
            GROUP BY category
            HAVING product_count > 50
        """)
        results = cursor.fetchall()
    
    agg_time = time.time() - start_time
    print(f"  ✅ 100次聚合查询: {agg_time:.3f}秒 ({agg_time/100*1000:.1f}ms/查询)")
    
    # 测试4: 更新操作
    print("📊 测试4: 更新操作性能")
    start_time = time.time()
    
    for i in range(0, 10000, 100):
        cursor.execute("""
            UPDATE products 
            SET stock = stock + 10, price = price * 1.01
            WHERE id BETWEEN ? AND ?
        """, (i, i + 99))
    
    conn.commit()
    update_time = time.time() - start_time
    print(f"  ✅ 100次批量更新: {update_time:.3f}秒 ({update_time/100*1000:.1f}ms/更新)")
    
    # 测试5: 事务性能
    print("📊 测试5: 事务性能")
    start_time = time.time()
    
    for _ in range(50):
        cursor.execute("BEGIN TRANSACTION")
        
        # 执行多个操作
        cursor.execute("SELECT COUNT(*) FROM products")
        count1 = cursor.fetchone()[0]
        
        cursor.execute("INSERT INTO products (name, barcode, category, price, cost, stock, alert_threshold) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      ("事务测试", "TX001", "测试", 99.9, 79.9, 10, 5))
        
        cursor.execute("DELETE FROM products WHERE name = '事务测试'")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        count2 = cursor.fetchone()[0]
        
        cursor.execute("COMMIT")
    
    transaction_time = time.time() - start_time
    print(f"  ✅ 50个事务: {transaction_time:.3f}秒 ({transaction_time/50*1000:.1f}ms/事务)")
    
    # 清理
    conn.close()
    shutil.rmtree(temp_dir)
    
    return {
        'insert_time': insert_time,
        'query_time': query_time,
        'agg_time': agg_time,
        'update_time': update_time,
        'transaction_time': transaction_time
    }

def benchmark_memory_usage():
    """基准测试内存使用"""
    print("\n💾 内存使用基准测试")
    print("=" * 50)
    
    try:
        import psutil
        psutil_available = True
    except ImportError:
        psutil_available = False
        print("⚠️ psutil不可用，使用简化内存监控")
    
    def get_memory_mb():
        if psutil_available:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                return 0
        else:
            import resource
            try:
                usage = resource.getrusage(resource.RUSAGE_SELF)
                memory_kb = usage.ru_maxrss
                if memory_kb > 10000:  # 可能是字节单位
                    memory_kb = memory_kb / 1024
                return memory_kb
            except:
                return 0
    
    # 记录内存基线
    baseline_memory = get_memory_mb()
    print(f"📊 内存基线: {baseline_memory:.1f}MB")
    
    # 创建大量数据
    conn, temp_dir, db_path = setup_test_db()
    cursor = conn.cursor()
    
    start_memory = get_memory_mb()
    
    # 插入大量数据
    large_data = []
    for i in range(50000):
        large_data.append((
            f"大数据产品{i:06d}",
            f"LRG{i:015d}",
            f"大数据类别{i%20}",
            100.0 + i,
            80.0 + i,
            50 + (i % 1000),
            10
        ))
    
    cursor.executemany("""
        INSERT INTO products (name, barcode, category, price, cost, stock, alert_threshold)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, large_data)
    conn.commit()
    
    peak_memory = get_memory_mb()
    memory_increase = peak_memory - start_memory
    
    print(f"📊 大量数据后: {peak_memory:.1f}MB")
    print(f"📊 内存增长: {memory_increase:.1f}MB ({memory_increase/50000*1000:.2f}KB/记录)")
    
    # 清理数据
    cursor.execute("DELETE FROM products")
    conn.commit()
    
    cleanup_memory = get_memory_mb()
    cleanup_delta = peak_memory - cleanup_memory
    
    print(f"📊 清理后: {cleanup_memory:.1f}MB")
    print(f"📊 内存回收: {cleanup_delta:.1f}MB")
    
    # 清理
    conn.close()
    shutil.rmtree(temp_dir)
    
    return {
        'baseline_memory': baseline_memory,
        'peak_memory': peak_memory,
        'memory_increase': memory_increase,
        'cleanup_delta': cleanup_delta
    }

def benchmark_system_import():
    """基准测试系统导入性能"""
    print("\n📦 系统导入性能基准测试")
    print("=" * 50)
    
    # 测试多次导入
    import_times = []
    
    for i in range(5):
        start_time = time.time()
        
        # 清除已缓存的模块
        modules_to_remove = [name for name in sys.modules.keys() 
                           if name.startswith('enhanced_sales_system') or name.startswith('config') or name.startswith('security')]
        for module_name in modules_to_remove:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        # 重新导入
        try:
            import enhanced_sales_system
            import_time = time.time() - start_time
            import_times.append(import_time)
            print(f"  ✅ 导入 {i+1}: {import_time:.3f}秒")
        except Exception as e:
            print(f"  ❌ 导入 {i+1} 失败: {e}")
            import_times.append(10.0)  # 失败则记为高时间
    
    avg_import_time = sum(import_times) / len(import_times)
    print(f"  📊 平均导入时间: {avg_import_time:.3f}秒")
    
    return {
        'import_times': import_times,
        'avg_import_time': avg_import_time
    }

def generate_performance_report(db_results, mem_results, import_results):
    """生成性能报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'database_performance': db_results,
        'memory_performance': mem_results,
        'import_performance': import_results,
        'summary': {
            'database_grade': 'A' if db_results['query_time'] < 1.0 else 'B' if db_results['query_time'] < 2.0 else 'C',
            'memory_grade': 'A' if mem_results['memory_increase'] < 50 else 'B' if mem_results['memory_increase'] < 100 else 'C',
            'import_grade': 'A' if import_results['avg_import_time'] < 1.0 else 'B' if import_results['avg_import_time'] < 2.0 else 'C',
            'overall_grade': 'A'
        }
    }
    
    # 计算总体评分
    grades = [report['summary']['database_grade'], 
             report['summary']['memory_grade'], 
             report['summary']['import_grade']]
    
    grade_scores = {'A': 3, 'B': 2, 'C': 1}
    avg_score = sum(grade_scores[g] for g in grades) / len(grades)
    
    if avg_score >= 2.5:
        report['summary']['overall_grade'] = 'A'
    elif avg_score >= 1.5:
        report['summary']['overall_grade'] = 'B'
    else:
        report['summary']['overall_grade'] = 'C'
    
    return report

def main():
    """主函数"""
    print("🌸 姐妹花销售系统 - 快速性能基准测试")
    print("=" * 60)
    print("专注于性能测试，不依赖GUI组件")
    print()
    
    # 运行基准测试
    db_results = benchmark_database_operations()
    mem_results = benchmark_memory_usage()
    import_results = benchmark_system_import()
    
    # 生成报告
    report = generate_performance_report(db_results, mem_results, import_results)
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📊 性能基准测试总结")
    print("=" * 60)
    
    print(f"🗄️  数据库性能: {report['summary']['database_grade']} 级")
    print(f"💾 内存使用: {report['summary']['memory_grade']} 级")
    print(f"📦 导入性能: {report['summary']['import_grade']} 级")
    print(f"🏆 总体评分: {report['summary']['overall_grade']} 级")
    
    print("\n📈 性能详情:")
    print(f"  • 插入性能: {10000/db_results['insert_time']:.0f} 记录/秒")
    print(f"  • 查询性能: {db_results['query_time']/1000*1000:.1f}ms/查询")
    print(f"  • 内存效率: {mem_results['memory_increase']/50000*1000:.2f}KB/记录")
    print(f"  • 导入时间: {import_results['avg_import_time']:.3f}秒")
    
    # 保存报告
    report_file = f"performance_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    # 性能建议
    print("\n💡 性能优化建议:")
    if report['summary']['database_grade'] == 'C':
        print("  • 考虑添加数据库索引优化查询性能")
    if report['summary']['memory_grade'] == 'C':
        print("  • 优化数据结构，减少内存占用")
    if report['summary']['import_grade'] == 'C':
        print("  • 考虑延迟导入或模块分割")
    
    if report['summary']['overall_grade'] == 'A':
        print("  🎉 系统性能表现优秀！")
    elif report['summary']['overall_grade'] == 'B':
        print("  👍 系统性能良好，可进一步优化")
    else:
        print("  ⚠️  系统性能需要优化")

if __name__ == "__main__":
    main()