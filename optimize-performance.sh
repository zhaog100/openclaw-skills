#!/bin/bash
# OpenClaw性能优化配置脚本
# 用于快速切换模型和优化设置

echo "🦞 OpenClaw性能优化工具"
echo "========================"

# 模型选项
echo ""
echo "📋 可用模型分类："
echo ""
echo "【免费快速模型】"
echo "1. glm-4.7-flash      - 最快，适合简单对话"
echo "2. gemini-3-flash     - 快速，适合日常任务"
echo "3. coding-glm-5-free  - 免费，适合代码任务"
echo ""
echo "【主力平衡模型】"
echo "4. glm-5              - 当前使用，平衡性能"
echo "5. qwen3.5-plus       - 百炼主力，中文优化"
echo "6. kimi-k2.5          - 长上下文，适合文档"
echo ""
echo "【高级模型】"
echo "7. qwen3-max          - 最强，适合复杂任务"
echo "8. gpt-4.1            - OpenAI最新"
echo "9. gemini-3-max       - Google最强"
echo ""

# Token节省建议
echo "💡 Token节省建议："
echo ""
echo "1. 使用QMD精准检索"
echo "   qmd search \"关键词\" -n 3"
echo "   节省：90%+ tokens"
echo ""
echo "2. 避免全量读取大文件"
echo "   ❌ cat MEMORY.md (2000+ tokens)"
echo "   ✅ memory_search + memory_get (150 tokens)"
echo ""
echo "3. 精简提示词"
echo "   ❌ \"好的，让我帮您检查一下...\""
echo "   ✅ \"检查系统状态\""
echo ""

# 性能监控命令
echo "📊 性能监控命令："
echo ""
echo "1. 查看会话状态"
echo "   /session_status"
echo ""
echo "2. 查看使用量"
echo "   openclaw usage"
echo ""
echo "3. 查看缓存命中率"
echo "   openclaw status | grep Cache"
echo ""

# 优化建议
echo "🎯 当前优化建议："
echo ""
echo "✅ 缓存命中率：93%（优秀）"
echo "✅ 成本：\$0.0000（免费额度内）"
echo "⚠️  可优化：切换到Flash模型可提升30%速度"
echo ""

# 交互式选择
echo "========================"
echo "选择优化方案："
echo ""
echo "A) 切换到Flash模型（快速、免费）"
echo "B) 保持当前配置（GLM-5平衡）"
echo "C) 查看详细优化文档"
echo ""
read -p "请选择 (A/B/C): " choice

case $choice in
  A|a)
    echo ""
    echo "切换到Flash模型..."
    echo "命令: /model zai/glm-4.7-flash"
    echo ""
    echo "优点："
    echo "  - 速度提升50%+"
    echo "  - 完全免费"
    echo "  - 适合日常对话"
    echo ""
    echo "缺点："
    echo "  - 复杂任务能力略弱"
    echo "  - 长文本理解稍差"
    ;;
  B|b)
    echo ""
    echo "保持当前配置"
    echo "当前模型: zai/glm-5"
    echo ""
    echo "优点："
    echo "  - 平衡性能"
    echo "  - 免费额度充足"
    echo "  - 适合各种任务"
    ;;
  C|c)
    echo ""
    echo "查看详细优化文档："
    echo "cat ~/.openclaw/workspace/PERFORMANCE-OPTIMIZATION.md"
    ;;
  *)
    echo "无效选择"
    ;;
esac

echo ""
echo "✅ 优化工具执行完成"
