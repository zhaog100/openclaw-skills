#!/bin/bash
# 模型自动选择脚本
# 根据任务类型推荐最合适的模型

# 任务类型特征识别
analyze_task() {
    local input="$1"
    local task_type=""
    local recommended_model=""

    # 关键词特征匹配
    if echo "$input" | grep -qiE "分析|推理|计算|思考|逻辑|论证|证明"; then
        task_type="深度思考"
        recommended_model="longcat/LongCat-Flash-Thinking-2601"
    elif echo "$input" | grep -qiE "写诗|写文|创作|剧本|小说|文案|内容"; then
        task_type="内容创作"
        recommended_model="longcat/LongCat-Flash-Chat"
    elif echo "$input" | grep -qiE "代码|编程|函数|算法|调试|bug|sql"; then
        task_type="代码生成"
        recommended_model="longcat/LongCat-Flash-Thinking-2601"
    elif echo "$input" | grep -qiE "图片|识别|看图|多模态|视觉"; then
        task_type="多模态理解"
        recommended_model="longcat/LongCat-Flash-Omni-2603"
    elif echo "$input" | grep -qiE "对话|聊天|交流|讨论|沟通"; then
        task_type="复杂对话"
        recommended_model="longcat/LongCat-Flash-Chat"
    elif echo "$input" | grep -qiE "查|搜索|找|问|简单|快速|简短"; then
        task_type="简单查询"
        recommended_model="longcat/LongCat-Flash-Lite"
    else
        task_type="未知任务"
        recommended_model="longcat/LongCat-Flash-Lite"
    fi

    echo "$task_type|$recommended_model"
}

# 主函数
main() {
    local input="$1"

    if [ -z "$input" ]; then
        echo "📋 模型自动选择指南："
        echo ""
        echo "🔥 轻量任务 (LongCat-Flash-Lite)"
        echo "   - 简单查询"
        echo "   - 快速响应"
        echo "   - 日常任务"
        echo ""
        echo "💬 对话任务 (LongCat-Flash-Chat)"
        echo "   - 复杂对话"
        echo "   - 内容创作"
        echo "   - 多轮交互"
        echo ""
        echo "🧠 思考任务 (LongCat-Flash-Thinking-2601)"
        echo "   - 深度思考"
        echo "   - 逻辑推理"
        echo "   - 代码生成"
        echo "   - 数学计算"
        echo ""
        echo "🖼️ 多模态 (LongCat-Flash-Omni-2603)"
        echo "   - 图片识别"
        echo "   - 多模态理解"
        echo ""
        echo "🎯 使用方式："
        echo "   /model <模型ID>"
        echo "   例如：/model longcat/LongCat-Flash-Chat"
        return 0
    fi

    local result=$(analyze_task "$input")
    local task_type=$(echo "$result" | cut -d'|' -f1)
    local model=$(echo "$result" | cut -d'|' -f2)

    echo "📊 任务分析："
    echo "   输入：$input"
    echo "   任务类型：$task_type"
    echo "   推荐模型：$model"
    echo ""
    echo "🎯 自动切换命令："
    echo "   /model $model"
}

main "$@"
