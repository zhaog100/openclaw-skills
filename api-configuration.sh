#!/bin/bash

# QMD API密钥配置和高级功能启用脚本

echo "🔧 QMD API密钥配置和高级功能启用"
echo "================================="

echo ""
echo "📋 当前状态检查:"
echo "✅ pi环境: pi v0.54.2 已安装"
echo "✅ qmd扩展: 已配置"
echo "❌ API密钥: 未配置"
echo ""

echo "🔑 API密钥配置方案:"
echo ""
echo "方案1: 环境变量方式 (推荐)"
echo "------------------------"
echo "在终端中执行:"
echo "export OPENAI_API_KEY='sk-your-openai-key'"
echo "export ZAI_API_KEY='sk-your-zai-key'"
echo ""

echo "方案2: 配置文件方式"
echo "--------------------"
echo "创建配置文件 ~/.pi/agent/config.json:"
echo '{'
echo '  "api_key": "sk-your-key",'
echo '  "provider": "openai"'
echo '}'
echo ""

echo "方案3: 免费API选项"
echo "--------------------"
echo "1. OpenAI (需要付费)"
echo "2. ZAI AI (有免费额度)"
echo "3. Gemini API (有免费额度)"
echo "4. Claude API (有免费额度)"
echo ""

echo "🚀 立即配置步骤:"
echo ""
echo "1. 获取API密钥:"
echo "   - 访问 https://platform.openai.com/ 获取OpenAI API密钥"
echo "   - 或访问 https://console.zhipu.com/ 获取ZAI API密钥"
echo ""

echo "2. 设置环境变量:"
echo "   export OPENAI_API_KEY='your-openai-key'"
echo "   export ZAI_API_KEY='your-zai-key'"
echo ""

echo "3. 验证配置:"
echo "   pi --list-models"
echo ""

echo "4. 测试高级功能:"
echo "   pi \"/qmd PMP认证\""
echo "   pi \"/qmd 敏捷方法\""
echo "   pi \"/qmd 测试工具\""
echo ""

echo "📊 预期效果:"
echo "✅ 启用AI增强搜索"
echo "✅ 智能文档分析"
echo "✅ 语义理解功能"
echo "✅ 高级内容推荐"
echo ""

echo "⚠️ 注意事项:"
echo "• 需要网络连接"
echo "• API密钥免费额度有限"
echo "• 建议先使用免费额度测试"
echo ""

echo "🎯 配置完成后即可启用高级功能！"
echo "建议先配置免费API密钥进行测试！"