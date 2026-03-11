#!/bin/bash
# 京东任务监控优化系统 - 一键运行脚本
# 版本: v1.0.0
# 创建时间: 2026-03-05

set -e

SCRIPTS_DIR="/ql/scripts"
LOG_DIR="/ql/data/log"

echo "🌾 京东任务监控优化系统"
echo "========================"
echo ""

# 创建日志目录
mkdir -p $LOG_DIR

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 显示菜单
show_menu() {
    echo "请选择要运行的功能："
    echo "1. 📊 日志监控（查看今日任务执行情况）"
    echo "2. 💰 收益优化（分析任务效率，推荐优化）"
    echo "3. 🎯 智能推荐（扫描可用任务，推荐新增）"
    echo "4. 🚀 一键运行全部（推荐）"
    echo "5. 📋 查看最新报告"
    echo "6. ⚙️ 配置管理"
    echo "0. 退出"
    echo ""
}

# 运行日志监控
run_monitor() {
    echo "📊 运行日志监控..."
    python3 $SCRIPTS_DIR/jd_task_monitor.py
    echo ""
}

# 运行收益优化
run_optimizer() {
    echo "💰 运行收益优化..."
    python3 $SCRIPTS_DIR/jd_earnings_optimizer.py
    echo ""
}

# 运行智能推荐
run_recommender() {
    echo "🎯 运行智能推荐..."
    python3 $SCRIPTS_DIR/jd_smart_recommender.py
    echo ""
}

# 查看最新报告
view_reports() {
    echo "📋 最新报告列表："
    echo ""
    
    # 监控报告
    monitor_report=$(ls -t $LOG_DIR/jd_monitor_report_*.txt 2>/dev/null | head -1)
    if [ -f "$monitor_report" ]; then
        echo "1. 监控报告: $(basename $monitor_report)"
        echo "   生成时间: $(stat -c %y "$monitor_report" | cut -d'.' -f1)"
    fi
    
    # 优化报告
    optimizer_report=$(ls -t $LOG_DIR/jd_optimizer_report_*.txt 2>/dev/null | head -1)
    if [ -f "$optimizer_report" ]; then
        echo "2. 优化报告: $(basename $optimizer_report)"
        echo "   生成时间: $(stat -c %y "$optimizer_report" | cut -d'.' -f1)"
    fi
    
    # 推荐报告
    recommender_report=$(ls -t $LOG_DIR/jd_recommender_report_*.txt 2>/dev/null | head -1)
    if [ -f "$recommender_report" ]; then
        echo "3. 推荐报告: $(basename $recommender_report)"
        echo "   生成时间: $(stat -c %y "$recommender_report" | cut -d'.' -f1)"
    fi
    
    echo ""
    read -p "输入编号查看详细报告 (0返回): " report_num
    
    case $report_num in
        1) cat "$monitor_report" | less ;;
        2) cat "$optimizer_report" | less ;;
        3) cat "$recommender_report" | less ;;
        0) return ;;
        *) echo "无效选择" ;;
    esac
}

# 配置管理
manage_config() {
    echo "⚙️ 配置管理"
    echo ""
    echo "1. 查看收益优化配置"
    echo "2. 查看智能推荐配置"
    echo "3. 编辑收益优化配置"
    echo "4. 编辑智能推荐配置"
    echo "0. 返回"
    echo ""
    read -p "请选择: " config_choice
    
    case $config_choice in
        1) cat /ql/data/config/jd_optimizer.json 2>/dev/null || echo "配置文件不存在" ;;
        2) cat /ql/data/config/jd_recommender.json 2>/dev/null || echo "配置文件不存在" ;;
        3) vim /ql/data/config/jd_optimizer.json ;;
        4) vim /ql/data/config/jd_recommender.json ;;
        0) return ;;
        *) echo "无效选择" ;;
    esac
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项: " choice
    echo ""
    
    case $choice in
        1)
            run_monitor
            ;;
        2)
            run_optimizer
            ;;
        3)
            run_recommender
            ;;
        4)
            echo "🚀 一键运行全部功能..."
            echo ""
            run_monitor
            run_optimizer
            run_recommender
            echo "✅ 全部完成！"
            ;;
        5)
            view_reports
            ;;
        6)
            manage_config
            ;;
        0)
            echo "👋 再见！"
            exit 0
            ;;
        *)
            echo "❌ 无效选项，请重新选择"
            ;;
    esac
    
    echo ""
    read -p "按回车继续..." dummy
    clear
done
