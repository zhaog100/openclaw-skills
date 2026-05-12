#!/usr/bin/env python3
"""
石油黄金统一报告生成器
合并所有报告功能，消除重复

功能整合：
- report.py (相关性分析)
- report_core.py (核心逻辑)
- report_text.py (文本报告)
- report_card.py (可视化卡片)

Copyright (c) 2026 思捷娅科技 (SJYKJ)
Author: 思捷娅科技 (SJYKJ)
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from fetch_fred_unified import get_all_macro_data
from analysis import load_data, run_all, interpret_correlation


def generate_correlation_analysis(period="1y", window=30):
    """生成相关性分析"""
    df = load_data(period)
    if df.empty:
        return {"error": "无法加载数据"}

    results = run_all(df, window)
    
    p = results["pearson"]
    s = results["spearman"]
    rc_now = results["rolling_current"]
    rc_range = results["rolling_range"]
    
    interpretation = interpret_correlation(p["pearson_r"])
    
    # 稳定性判断
    if rc_range[1] - rc_range[0] > 0.3:
        stability = "波动较大，相关关系不稳定"
    elif rc_range[1] - rc_range[0] > 0.15:
        stability = "存在一定波动"
    else:
        stability = "相对稳定"
    
    return {
        "pearson_r": p["pearson_r"],
        "pearson_p": p.get("pearson_p", 0.0),
        "spearman_r": s["spearman_r"],
        "spearman_p": s.get("spearman_p", 0.0),
        "rolling_current": rc_now,
        "rolling_range": rc_range,
        "interpretation": interpretation,
        "stability": stability,
        "significance": p.get("significance", False)
    }


def generate_market_analysis():
    """生成市场分析"""
    try:
        from advisor import _analyze_instrument
        
        gold_result = _analyze_instrument('沪金期货', period="90d", horizon=3)
        oil_result = _analyze_instrument('沪油期货', period="90d", horizon=3)
        
        return {
            "gold": gold_result,
            "oil": oil_result
        }
    except Exception as e:
        return {"error": f"市场分析失败: {e}"}


def generate_macro_analysis():
    """生成宏观分析"""
    try:
        return get_all_macro_data()
    except Exception as e:
        return {"error": f"宏观数据获取失败: {e}"}


def format_text_report(correlation_data, market_data, macro_data):
    """生成文本报告"""
    lines = []
    
    # 标题
    lines.append(f"石油黄金投资分析报告 {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("=" * 50)
    
    # 相关性分析
    if "error" not in correlation_data:
        lines.append("\n📊 相关性分析")
        lines.append("-" * 20)
        lines.append(f"Pearson相关系数: {correlation_data['pearson_r']:.4f}")
        lines.append(f"Spearman秩相关: {correlation_data['spearman_r']:.4f}")
        lines.append(f"30日滚动相关: {correlation_data['rolling_current']:.4f}")
        lines.append(f"稳定性: {correlation_data['stability']}")
        lines.append(f"解读: {correlation_data['interpretation']}")
    
    # 市场分析
    if "error" not in market_data:
        lines.append("\n🎯 市场分析")
        lines.append("-" * 20)
        if market_data.get("gold"):
            gold = market_data["gold"]
            lines.append(f"🥇 黄金: {gold.get('score', 0)}/100 - {gold.get('verdict', 'N/A')}")
        if market_data.get("oil"):
            oil = market_data["oil"]
            lines.append(f"🛢️ 原油: {oil.get('score', 0)}/100 - {oil.get('verdict', 'N/A')}")
    
    # 宏观分析
    if "error" not in macro_data:
        lines.append("\n💡 宏观信号")
        lines.append("-" * 20)
        
        conf = macro_data.get('consumer_confidence')
        if conf:
            lines.append(f"消费者信心: {conf['value']}")
        else:
            lines.append("消费者信心: [数据不可用]")
            
        vix = macro_data.get('vix')
        if vix:
            lines.append(f"VIX恐慌指数: {vix['value']}")
        else:
            lines.append("VIX恐慌指数: [数据不可用]")
    
    lines.append("\n⚠️ 仅供参考，不构成投资建议")
    
    return "\n".join(lines)


def generate_visual_card(market_data, macro_data):
    """生成可视化卡片 (调用原有report_card逻辑)"""
    try:
        # 导入原有report_card功能
        from report_card import draw_report
        
        # 准备数据
        results = {}
        tech_scores = {}
        
        if market_data.get("gold"):
            results['沪金期货'] = market_data["gold"]
            tech_scores['沪金期货'] = market_data["gold"].get('score', 50)
            
        if market_data.get("oil"):
            results['沪油期货'] = market_data["oil"]
            tech_scores['沪油期货'] = market_data["oil"].get('score', 50)
        
        # 风险评分
        risk_score = 50
        try:
            from geopolitics import generate_geopolitical_section
            _, risk_score = generate_geopolitical_section()
        except:
            pass
        
        # 生成卡片
        return draw_report(results, tech_scores, risk_score)
        
    except Exception as e:
        return f"可视化卡片生成失败: {e}"


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="石油黄金统一报告生成器")
    parser.add_argument("--type", choices=["text", "visual", "json", "all"], default="text", 
                       help="报告类型: text(文本), visual(可视化), json(JSON), all(全部)")
    parser.add_argument("--period", default="1y", help="数据周期")
    parser.add_argument("--window", type=int, default=30, help="滚动窗口")
    
    args = parser.parse_args()
    
    # 生成各类分析数据
    correlation_data = generate_correlation_analysis(args.period, args.window)
    market_data = generate_market_analysis()
    macro_data = generate_macro_analysis()
    
    if args.type in ["text", "all"]:
        text_report = format_text_report(correlation_data, market_data, macro_data)
        print(text_report)
        
        # 保存文本报告
        from config import REPORT_TEXT, ensure_dirs
        ensure_dirs()
        with open(REPORT_TEXT, 'w') as f:
            f.write(text_report)
        print(f"\n文本报告已保存: {REPORT_TEXT}")
    
    if args.type in ["json", "all"]:
        import json
        json_report = {
            "correlation_analysis": correlation_data,
            "market_data": market_data,
            "macro_data": macro_data,
            "timestamp": datetime.now().isoformat(),
            "period": args.period,
            "window": args.window
        }
        print(json.dumps(json_report, ensure_ascii=False, indent=2))
        
        # 保存JSON报告
        json_path = Path(__file__).parent.parent / "reports" / "oil-gold-report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, ensure_ascii=False, indent=2)
        print(f"\nJSON报告已保存: {json_path}")
    
    if args.type in ["visual", "all"]:
        card_path = generate_visual_card(market_data, macro_data)
        if isinstance(card_path, str) and card_path.endswith(('.jpg', '.png')):
            print(f"可视化卡片已生成: {card_path}")
        else:
            print(f"可视化卡片生成失败: {card_path}")


if __name__ == "__main__":
    main()