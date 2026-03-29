#!/usr/bin/env python3
"""
模型性能验证
验证智能模型切换的效果
"""

import pandas as pd
import os
from datetime import datetime
from deepchecks.tabular import Dataset, TrainTestSuite
from deepchecks.tabular.checks import (
    TrainTestPerformance,
    TrainTestLabelDrift,
    ModelInferenceTime,
    BoostingOverfit,
    FeatureLabelCorrelation
)

WORKSPACE = '/home/zhaog/.openclaw/workspace'
LOGS_DIR = os.path.join(WORKSPACE, 'logs')

def generate_mock_model_data(n_samples=100):
    """生成模拟模型切换数据"""
    import random
    
    models = ['glm-5', 'qwen3.5-plus', 'gemini-flash', 'claude-3.5']
    topics = ['技术问题', '日常对话', '代码开发', '文档写作', '数据分析']
    
    data = []
    for i in range(n_samples):
        model = random.choice(models)
        data.append({
            'model_type': model,
            'response_time': random.uniform(0.5, 5.0),
            'accuracy': random.uniform(0.7, 1.0),
            'user_satisfaction': random.randint(1, 5),
            'topic': random.choice(topics),
            'word_count': random.randint(100, 5000),
            'timestamp': datetime.now().timestamp() - random.randint(0, 86400*7)
        })
    
    return pd.DataFrame(data)

def validate_model_performance():
    """验证模型性能"""
    print("=" * 60)
    print("🤖 模型性能验证")
    print("=" * 60)
    print()
    
    # 创建日志目录
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 尝试加载真实日志
    log_file = os.path.join(LOGS_DIR, 'model-switch.log')
    
    if os.path.exists(log_file):
        print(f"📂 加载日志文件：{log_file}")
        try:
            data = pd.read_csv(log_file)
            print(f"✅ 加载成功：{len(data)} 条记录")
        except Exception as e:
            print(f"⚠️  加载失败：{e}")
            print("📝 使用模拟数据演示")
            data = generate_mock_model_data()
    else:
        print("⚠️  日志文件不存在")
        print("📝 使用模拟数据演示")
        data = generate_mock_model_data()
    
    print()
    
    # 数据预览
    print("📊 数据概览：")
    print("-" * 60)
    print(f"  总记录数：{len(data)}")
    print(f"  模型种类：{data['model_type'].nunique()}")
    print(f"  平均响应时间：{data['response_time'].mean():.2f}秒")
    print(f"  平均准确率：{data['accuracy'].mean():.2%}")
    print(f"  平均满意度：{data['user_satisfaction'].mean():.1f}/5")
    print()
    
    # 创建数据集
    print("🔧 创建数据集...")
    dataset = Dataset(
        data,
        label='user_satisfaction',
        cat_features=['model_type', 'topic'],
        numerical_features=['response_time', 'accuracy', 'word_count']
    )
    print("✅ 数据集创建完成")
    print()
    
    # 创建验证套件
    print("📦 创建验证套件...")
    suite = TrainTestSuite()
    
    # 添加检查项
    suite.add(TrainTestPerformance())
    suite.add(TrainTestLabelDrift())
    suite.add(ModelInferenceTime())
    suite.add(BoostingOverfit())
    suite.add(FeatureLabelCorrelation())
    
    print("✅ 已添加 5 个检查项：")
    print("   1. TrainTestPerformance - 训练测试性能对比")
    print("   2. TrainTestLabelDrift - 标签漂移检测")
    print("   3. ModelInferenceTime - 模型推理时间")
    print("   4. BoostingOverfit - 过拟合检测")
    print("   5. FeatureLabelCorrelation - 特征标签相关性")
    print()
    
    # 运行验证
    print("🔬 正在运行模型验证...")
    try:
        result = suite.run(dataset)
        print("✅ 验证完成！")
        print()
        
        # 保存结果
        report_path = os.path.join(LOGS_DIR, 'model-performance-report.html')
        result.save_as_html(report_path)
        
        print("=" * 60)
        print("✅ 模型验证完成！")
        print("=" * 60)
        print()
        print(f"📄 报告已保存：{report_path}")
        print()
        print("💡 建议：在浏览器中打开 HTML 报告查看详细分析")
        print(f"   firefox {report_path}")
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ 验证失败：{e}")
        print()
        print("💡 提示：这可能是因为数据集太小或格式问题")
        print("   在实际使用中，请确保有足够的历史数据")
        print()
        return None

def compare_models():
    """比较不同模型的性能"""
    print("=" * 60)
    print("📊 模型性能对比")
    print("=" * 60)
    print()
    
    # 生成模拟数据
    data = generate_mock_model_data(500)
    
    # 按模型分组统计
    print("📈 各模型性能统计：")
    print("-" * 60)
    
    grouped = data.groupby('model_type').agg({
        'response_time': 'mean',
        'accuracy': 'mean',
        'user_satisfaction': 'mean',
        'word_count': 'mean'
    }).round(2)
    
    print(grouped.to_string())
    print()
    
    # 找出最佳模型
    best_model = grouped['user_satisfaction'].idxmax()
    print(f"🏆 用户满意度最高：{best_model} ({grouped.loc[best_model, 'user_satisfaction']}/5)")
    
    fastest_model = grouped['response_time'].idxmin()
    print(f"⚡ 响应速度最快：{fastest_model} ({grouped.loc[fastest_model, 'response_time']}秒)")
    
    most_accurate = grouped['accuracy'].idxmax()
    print(f"🎯 准确率最高：{most_accurate} ({grouped.loc[most_accurate, 'accuracy']:.1%})")
    print()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--compare':
        compare_models()
    else:
        validate_model_performance()
